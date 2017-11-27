from collections import OrderedDict
import matplotlib.pyplot as plt
import networkx
import datetime
import re

from .ActionPlanner import ActionPlanner, Noop, Success
from .KnowledgeMap import KnowledgeMap
from .Blackboard import Blackboard, QueryBuilder
from .QueryParser import QueryParser
from .ConnectionPGM import ConnectionPGM
from .actions.eutils import PubmedEdgeStats

class Agent:
    """
    Generate a reasoning agent to answer a provided question.
    
    The agent will attempt to answer an input question in four steps:
    1. parse the input question using natural-language processing
    2. create a plan to acquire knowledge
    3. execute and, if necessary, iteratively adapt the plan
    4. analyze the acquired knowledge and return an answer if one was found.

    Parameters
    ----------
    
    question : str
       A question the agent should answer, formulated in English.
       
    discount : float
       Discount value used by the MDP value iteration algorithm to find
       a knowledge acquisiton plan. Must be in range [0,1].

    """
    def __init__(self, question, discount = 0.4):
        self.parser = QueryParser()
        self.blackboard = Blackboard()
        self.discount = discount
        query = self.parser.parse(question)
        if len(query) == 0:
            print('Query could not be parsed.')
            return None
        
        km = KnowledgeMap()
        if query['relation']['term'] in ('clinical outcome pathway', 'outcome pathway','clinical outcome path', 'outcome path'):
            km.load_module('outcome_path')
        elif query['relation']['term'] in ('protect', 'protects'):
            km.load_module('protects_from')
        
        self.planner = ActionPlanner(km, km.default_goal)
        self.planner.make_plan(self.discount)
        
        if query['from']['bound'] == True:
            self.blackboard.add_node(query['from']['term'], entity = query['from']['entity'], name = query['from']['term'])
            
        if query['to']['bound'] == True:
            self.blackboard.add_node(query['to']['term'], entity = query['to']['entity'], name = query['to']['term'])

    def show_blackboard(self, width=2, height=2):
        """Plot a figure showing the current blackboard content.
        
        Parameters
        ----------
        width : numeric, optional
            width of plot (default: 2)
        
        height : numeric, optional
            height of plot (default: 2)
        
        """
        plt.figure(figsize=(width, height))
        networkx.draw(self.blackboard, with_labels=True)
    
    def get_state(self, graph):
        entities = set(d['entity'] for n,d in graph.nodes(data=True) if not 'unbound' in d)
        bound_nodes = set('bound(' + e + ')' for e in entities if e is not None)
        connections = set(self.planner.get_canonical_state_variable('connected(' + ', '.join(d['entities']) + ')') for u,v,d in graph.edges(data=True))
        return({'state':bound_nodes|connections, 'entities':entities})
    
    def observe_state(self):
        """Return the current agent state.
        
        Returns
        -------
        dict
            A dictionary with entries 'state' and 'entities', which are lists of the
            current state variables and the unique entities they contain, respectively.
        
        """
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
        """Execute the current plan to query knowledge sources.
        
        Returns
        -------
        bool
            True if knowledge acquisition was successful (i.e., the agent reached
            a goal state), False if not.
        
        """
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

    def set_edge_stats(self, path_graph):
        pubmed = PubmedEdgeStats()
        variant_pattern = re.compile("\((.*)\):")
        stats = dict()
        ph = set(self.blackboard.placeholders)
        for (u, v) in path_graph.edges():
            if len({u,v} & ph) == 0:
                start = u
                end = v
                
                ## extract the gene name if it's a variant
                if self.blackboard.nodes[u]['entity'] == 'Variant':
                    m = variant_pattern.search(u)
                    if m is not None:
                        start = m.group(1)
                    else:
                        print(u)
                
                if self.blackboard.nodes[v]['entity'] == 'Variant':
                    m = variant_pattern.search(v)
                    if m is not None:
                        end = m.group(1)
                    else:
                        print(v)
                    
                stats[(u,v)] = pubmed.get_edge_stats(start,end)  
        
        # use path graph to iterate but apply updates to blackboard
        networkx.set_edge_attributes(self.blackboard, stats)

    def calculate_edge_probabilities(self):
        pgm = ConnectionPGM()
        variables = ['is_connection']
        
        evidence_types = ('pubmed',)
        
        # calculate default probabilities
        default_probabilities = dict()
        for evidence_type in evidence_types:
            samples = pgm.evaluate(evidence_type, {}, variables)
            default_probabilities[evidence_type] = pgm.get_mean(samples, 'is_connection')
        
        current_year = int(datetime.datetime.now().year)
        attributes = dict()
        for (u, v, d) in self.blackboard.edges(data=True):
            if 'article_count' not in d or d['article_count'] == 0:
                sample_mean = default_probabilities['pubmed']
            else:
                evidence = {'num_articles':d['article_count']}
                if 'year_first_article' in d:
                    y = current_year - d['year_first_article']
                    evidence['years_since_first_article'] = y
                samples = pgm.evaluate('pubmed', evidence, variables)
                sample_mean = pgm.get_mean(samples, 'is_connection')
                
            # add 1 to cost because the default cost in networx is 1
            attributes[(u,v)] = {'p':sample_mean,'cost':1+(1-sample_mean)}
        networkx.set_edge_attributes(self.blackboard, attributes)

    def in_goal_state(self):
        """Returns True if the agent is in a goal state.
        
        Returns
        -------
        boolean
            Indicates whether the agent is in a goal state or not.
        
        """
        current_state = self.observe_state()['state']
        diff = set(self.planner.goal_state) - set(current_state)
        return len(diff) == 0
    
    def analyze(self, source, target):
        """Analyze the knowledge on the blackboard and return the best path between source and target.
        
        Parameters
        ----------
        source : str
            Name of the source node.
            
        target : str
            Name of the target node.
        
        Returns
        -------
        path : dict
            A dictionary with entries 'nodes' and 'edges', each of which is a list of path elements,
            listed in the order from source to target. Each node is represented by a dictionary of
            node attributes, minimally including its 'name' and 'entity'. Similarly, each edge has a
            dictionary with attributes, minimally its probability 'p'. If no path was found, an
            empty dictionary is returned.
        
        """
        # create a subgraph that consists of all nodes on a path between source and target
        path_graph = self.blackboard.get_path_subgraph([source], [target])
        self.set_edge_stats(path_graph)
        self.calculate_edge_probabilities()
        try:
            path_nodes = networkx.shortest_path(self.blackboard, source, target, 'cost')
            path = {'nodes':[], 'edges':[]}
            for i in range(len(path_nodes)):
                attributes = self.blackboard.nodes[path_nodes[i]].copy()
                if 'unbound' in attributes and attributes['unbound'] == True:
                    attributes['name'] = re.sub(r'_[0-9]+?$', '', attributes['name'])
                path['nodes'].append(attributes)
                if i < (len(path_nodes)-1):
                    path['edges'].append(self.blackboard.edges[path_nodes[i], path_nodes[i+1]])
            return path
        except networkx.NetworkXNoPath:
            print("No path exists.")
            return {}
