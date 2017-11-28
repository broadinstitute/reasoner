import ipywidgets as widgets
import matplotlib.pyplot as plt
import networkx

from reasoner.ActionPlanner import ActionPlanner, Noop, Success
from reasoner.KnowledgeMap import KnowledgeMap
from reasoner.Blackboard import Blackboard, QueryBuilder
from reasoner.QueryParser import QueryParser

from reasoner.actions.eutils import PubmedDrugDiseasePath
from reasoner.Agent import Agent

from .actions.edit_actions import *
from .actions.eutils import *
from .actions.sparql import *
from .actions.pharos import *
from .actions.file_actions import *

import os
import sys

    
pubmed_path = {
                    'actions': 
                        [                                              
                            {
                                'action':PubmedDrugDiseasePath(),
                                'p_success':0.7,
                                'reward':3
                            }
                        ],

                    'state_vars':
                        ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)',
                         'bound(Disease)', 'connected(Drug, Target)', 'connected(Target, Pathway)',
                         'connected(Pathway, Cell)', 'connected(Cell, Symptom)', 'connected(Symptom, Disease)'],

                    'goal_state':
                        ['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)',
                         'bound(Disease)', 'connected(Drug, Target)', 'connected(Target, Pathway)',
                         'connected(Pathway, Cell)', 'connected(Cell, Symptom)', 'connected(Symptom, Disease)']
}

def run_query(question):
    print("Initializing and planning ...")
    agent = DemoAgent(question)
    
    print("Querying knowledge sources ...")
    agent.acquire_knowledge()
    
    print("Analyzing ...")
    agent.blackboard.prune(sources = [agent.query['from']['term']], targets = [agent.query['to']['term']], remove_placeholders = True)
    outcome_pathway = agent.analyze(agent.query['from']['term'], agent.query['to']['term'])

    p_total = 1
    for e in outcome_pathway['edges']:
        p_total = p_total*max(e['p'], 0.001)

    print("done\n\nResults:")
    for node in outcome_pathway['nodes']:
        print(node['entity'] + ': ' + node['name'])

    print('\nprobability: ' + str(p_total))
    
    agent.show_blackboard(15, 12)
    
def handle(sender):
    print(question.value)
    run_query(question.value)
    
class DemoAgent(Agent):
    def __init__(self, question, discount = 0.4):
        self.parser = QueryParser()
        self.blackboard = Blackboard()
        self.discount = discount
        self.query = self.parser.parse(question)
        if len(self.query) == 0:
            print('Query could not be parsed.')
            return None
        
        km = KnowledgeMap()
        km.load_module(pubmed_path)

        
        self.planner = ActionPlanner(km, km.default_goal)
        self.planner.make_plan(self.discount)
        
        if self.query['from']['bound'] == True:
            self.blackboard.add_node(self.query['from']['term'], entity = self.query['from']['entity'], name = self.query['from']['term'])
            
        if self.query['to']['bound'] == True:
            self.blackboard.add_node(self.query['to']['term'], entity = self.query['to']['entity'], name = self.query['to']['term'])

def start_agent():
    print('\n')
    display(question)
    print('\n\n')
    
question = widgets.Text(placeholder='Enter a question', disabled=False)
question.on_submit(handle)

