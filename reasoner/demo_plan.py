import numpy
import scipy
from reasoner.ActionPlanner import ActionPlanner
from reasoner.KnowledgeMap import KnowledgeMap
from reasoner.actions.test import *
from pprint import pprint


def action_name(action):
    print(type(action).__name__)


test1 = {
    'actions':
        [
            {
                'action':AddDrugTarget(),
                'p_success':0.8,
                'reward':1
            }
        ],
    'state_vars':[
            'bound(Drug)',
            'bound(Target)',
            'connected(Drug, Target)'
        ],
    'goal_state':[
            'bound(Drug)',
            'bound(Target)',
            'connected(Drug, Target)'
        ]
}


test2 = {
    'actions':
        [
            {
                'action':AddDrugTarget_Good(),
                'p_success':0.3,
                'reward':3
            },

            {
                'action':AddDrugTarget_Mediocre(),
                'p_success':0.9,
                'reward':1
            },

            {
                'action':AddTargetPathway(),
                'p_success':0.5,
                'reward':1
            }
        ],
    'state_vars':[
            'bound(Drug)',
            'bound(Target)',
            'bound(Pathway)',
            'connected(Drug, Target)',
            'connected(Target, Pathway)'
        ],
    'goal_state':[
            'bound(Drug)',
            'bound(Target)',
            'bound(Pathway)',
            'connected(Drug, Target)',
            'connected(Target, Pathway)'
        ]
}