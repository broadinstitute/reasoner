from collections import OrderedDict
import matplotlib.pyplot as plt
import networkx
import datetime

from .ActionPlanner import ActionPlanner, Noop, Success
from .KnowledgeMap import KnowledgeMap
from .Blackboard import Blackboard, QueryBuilder
from .QueryParser import QueryParser
from .ConnectionPGM import ConnectionPGM

from .actions.eutils import *
from .actions.sparql import *
from .actions.pharos import PharosDrugToTarget
from .actions.file_actions import *

class Agent:
    def __init__(self, question, discount = 0.4, state_action_tuple=None):
        self.parser = QueryParser()
        self.blackboard = Blackboard()
        self.discount = discount
        query = self.parser.parse(question)

        if state_action_tuple is not None:
          (action_list, state_vars, goal_state) = state_action_tuple
        else:
          (action_list, state_vars, goal_state) = self.get_lists()
        self.planner = ActionPlanner(KnowledgeMap(state_vars, action_list), goal_state)
        self.planner.make_plan(self.discount)
        
        if query['from']['bound'] == True:
            self.blackboard.add_node(query['from']['term'], entity = query['from']['entity'])
            
        if query['to']['bound'] == True:
            self.blackboard.add_node(query['to']['term'], entity = query['to']['entity'])

    def show_blackboard(self, width=2, height=2):
        plt.figure(figsize=(width, height))
        networkx.draw(self.blackboard, with_labels=True)
    
    def get_state(self, graph):
        entities = set(d['entity'] for n,d in graph.nodes(data=True) if not 'unbound' in d)
        bound_nodes = set('bound(' + e + ')' for e in entities)
        connections = set(self.planner.get_canonical_state_variable('connected(' + ', '.join(d['entities']) + ')') for u,v,d in graph.edges(data=True))
        return({'state':bound_nodes|connections, 'entities':entities})
    
    def observe_state(self):
        return(self.get_state(self.blackboard))
  
    def observe_path_state(self, start, end):
        if not networkx.has_path(self.blackboard, start, end):
            # perform "union" check
            return(self.get_state(self.blackboard))
        else:
            # check each path individually
            path_states = list()
            for path in networkx.all_shortest_paths(self.blackboard, source=start, target=end):
                sg = self.blackboard.subgraph(path)
                path_states.append(self.get_state(sg))
            return(path_states)
    
    def acquire_knowledge(self):
        # guard agains external changes to blackboard
        if len(self.planner.actions_used) > 0:
            print("Blackboard may have changed since last knowledge acquisition ... replanning")
            self.planner.replan(self.discount)
        
        current_state = self.observe_state()
        next_action = self.planner.get_action(current_state['state'])

        while not isinstance(next_action, Success):
            print('current state: ' + str(current_state['state']))
            print('next action: ' + type(next_action).__name__)
            
            if isinstance(next_action, Noop):
                print("No connections found.")
                return False
            
            queries = QueryBuilder().get_queries(self.blackboard.get_entity_nodes(next_action.precondition_entities))
            for query in queries:
                result = next_action.execute(query)
                self.blackboard.add_knowledge(query, result, next_action)
            self.planner.set_action_used(next_action)
            
            previous_state = current_state
            current_state = self.observe_state()
            #observed_changes = current_state - previous_state
            #expected_changes = set(next_action.effect_terms) - set(next_action.precondition)
            #if not any([x in current_state['entities'] for x in expected_changes]):
            if current_state['state'] == previous_state['state']:
                print('action failed ... replanning')
                self.planner.replan(self.discount)

            next_action = self.planner.get_action(current_state['state'])
            if self.planner.was_action_used(next_action) == True:
                print('action failed ... replanning')
                self.planner.replan(self.discount)
                next_action = self.planner.get_action(current_state['state'])
        return True

    def set_edge_stats(self):
        pubmed = PubmedEdgeStats()
        stats = dict()
        ph = set(self.blackboard.placeholders)
        for (u, v) in self.blackboard.edges():
            if len({u,v} & ph) == 0:
                stats[(u,v)] = pubmed.get_edge_stats(u,v)                
        networkx.set_edge_attributes(self.blackboard, attributes)

    def calculate_edge_probabilities(self, default_probability = 1/1000):
        pgm = ConnectionPGM()
        variables = ['is_connection']

        current_year = int(datetime.datetime.now().year)
        attributes = dict()
        for (u, v, d) in self.blackboard.edges(data=True):
            if 'article_count' not in d or d['article_count'] == 0:
                attributes[(u,v)] = {'p':default_probability,'1-p':1-default_probability}
            else:
                evidence = {'num_articles':d['article_count']}
                if 'year_first_article' in d:
                    y = current_year - d['year_first_article']
                    evidence['years_since_first_article'] = y
                samples = pgm.evaluate('pubmed', evidence, variables)
                sample_mean = pgm.get_mean(samples, 'is_connection')
                attributes[(u,v)] = {'p':sample_mean,'1-p':1-sample_mean}
                #print(u + ' ' + v + ' ' + str(pgm.get_mean(samples, 'is_connection')))
        networkx.set_edge_attributes(self.blackboard, attributes)

    def in_goal_state(self):
        current_state = self.observe_state()['state']
        diff = set(self.planner.goal_state) - set(current_state)
        return(len(diff) == 0)
    
    def analyze(self, sources, targets):
        # create a subgraph that consists of all nodes on a path between source and target
        #path_graph = self.blackboard.get_path_subgraph()
        
        self.set_edge_stats()
        self.calculate_edge_probabilities()
        return(networkx.shortest_path(self.blackboard, sources, targets, '1-p'))

    def get_lists(self):
        action_list =[
            {
                'action':DrugBankDrugToTarget(),
                'p_success':0.5,
                'reward':2
            },
            
            {
                'action':PharosDrugToTarget(),
                'p_success':0.5,
                'reward':1
            },

            {
                'action':GoFunctionTargetToPathway(),
                'p_success':0.7,
                'reward':1.2
            },

            {
                'action':WikiPWTargetToPathway(),
                'p_success':0.6,
                'reward':2
            },

            {
                'action':PubmedPathwayDiseasePath(),
                'p_success':0.9,
                'reward':2
            },

               {
                'action':PubmedCellDiseasePath(),
                'p_success':0.9,
                'reward':1
            },

            {
                'action':PubmedDiseaseToSymptom(),
                'p_success':0.9,
                'reward':0.5
            },

            {
                'action':PubmedDrugDiseasePath(),
                'p_success':0.99,
                'reward':0.5
            }
        ]

        state_vars =  ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'bound(Disease)',
                      'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Symptom)', 'connected(Symptom, Disease)']


        goal_state = ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'bound(Disease)',
                                 'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Symptom)', 'connected(Symptom, Disease)']

        return((action_list, state_vars, goal_state))