from collections import OrderedDict
import matplotlib.pyplot as plt
import networkx
import datetime

from .ActionPlanner import ActionPlanner, Noop, Success
from .KnowledgeMap import KnowledgeMap
from .Blackboard import Blackboard, QueryBuilder
from .QueryParser import QueryParser
from .ConnectionPGM import ConnectionPGM

from .actions.pubmed import *
from .actions.sparql_actions import *
from .actions.pharos import PharosDrugToTarget
from .actions.file_actions import *

class Agent:
    def __init__(self, question, discount = 0.4, state_action_tuple=None):
        self.parser = QueryParser()
        self.blackboard = Blackboard()
        query = self.parser.parse(question)
        
        if state_action_tuple is not None:
          (action_list, state_vars, goal_state) = state_action_tuple
        else:
          (action_list, state_vars, goal_state) = self.get_lists()
        self.planner = ActionPlanner(KnowledgeMap(state_vars, action_list), goal_state)
        self.planner.make_plan(discount)
        
        self.blackboard.add_node(query['from']['term'], entity = query['from']['entity'])
        self.blackboard.add_node(query['to']['term'], entity = query['to']['entity'])

    def show_blackboard(self, width=2, height=2):
        plt.figure(figsize=(width, height))
        networkx.draw(self.blackboard, with_labels=True)
        
    def acquire_knowledge(self):
        current_state = self.blackboard.observe_state()
        next_action = self.planner.get_action(current_state['state'])

        while not isinstance(next_action, Success):
            print(current_state['state'])
            print(type(next_action).__name__)
            queries = QueryBuilder().get_queries(self.blackboard.get_entity_nodes(next_action.precondition_entities))
            for query in queries:
                result = next_action.execute(query)
                self.blackboard.add_knowledge(query, result, next_action)

            current_state = self.blackboard.observe_state()
            if not any([x in current_state['entities'] for x in (set(next_action.effect_entities) - set(next_action.precondition_entities))]):
                print('action failed ... replanning')
                self.planner.replan()

            next_action = self.planner.get_action(current_state['state'])
            if isinstance(next_action, Noop):
                print("No connections found.")
                break
                
    def set_edge_stats(self):
        stats = PubmedEdgeStats()
        attributes = {(u,v):stats.get_edge_stats(u,v) for (u, v) in self.blackboard.edges()}
        networkx.set_edge_attributes(self.blackboard, attributes)
    
    def calculate_edge_probabilities(self):
        pgm = ConnectionPGM()
        variables = ['is_connection']

        current_year = int(datetime.datetime.now().year)
        attributes = dict()
        for (u, v, d) in self.blackboard.edges(data=True):
            y = current_year - d['year_first_article']
            samples = pgm.evaluate('pubmed',
                                  {'num_articles':d['article_count'],
                                   'years_since_first_article':y}, variables)
            sample_mean = pgm.get_mean(samples, 'is_connection')
            attributes[(u,v)] = {'p':sample_mean,'1-p':1-sample_mean}
            #print(u + ' ' + v + ' ' + str(pgm.get_mean(samples, 'is_connection')))
        networkx.set_edge_attributes(self.blackboard, attributes)
    
    def analyze(self, source, target):
        self.set_edge_stats()
        self.calculate_edge_probabilities()
        return(networkx.shortest_path(self.blackboard, source, target, '1-p'))
    
    def get_lists(self):
        action_list =[
            {
                'action':DrugBankDrugToTarget(),
                'p_success':0.5,
                'reward':2
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
                'action':PubmedDiseaseToPhenotype(),
                'p_success':0.9,
                'reward':0.5
            },

            {
                'action':PubmedDrugDiseasePath(),
                'p_success':0.99,
                'reward':2
            }   
        ]

        state_vars =  ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'bound(Disease)',
                      'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Phenotype)', 'connected(Phenotype, Disease)']


        goal_state = ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'bound(Disease)',
                                 'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Phenotype)', 'connected(Phenotype, Disease)']

        return((action_list, state_vars, goal_state))