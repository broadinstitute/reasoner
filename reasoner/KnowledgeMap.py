from .actions.edit_actions import *
from .actions.eutils import *
from .actions.sparql import *
from .actions.pharos import *
from .actions.file_actions import *


class KnowledgeMap:
    """
    Store query actions and other information of how to interact with knowledge sources.
    
    The ``KnowledgeMap`` is a central repository for ``Action`` objects and their quality
    metrics. The quality metrics are the (1) transition probabilities and (2) rewards used
    by the ``ActionPlanner`` to calculate a plan (using a Markov decision process).

    """
    def __init__(self):
        pass
        
    def load_module(self, module):
        """Load a module into a ``KnowledgeMap`` object.
        
        Parameters
        ----------
        module : str
            The name of the module to be loaded.
        
        """
        
        if isinstance(module, dict):
            self.state_variables = module['state_vars']
            self.actions = module['actions']
            self.default_goal = module['goal_state']
        else:
            modules = {
                'protects_from':{
                    'actions':
                        [
                            {
                                'action':EditGeneticConditionToDisease(),
                                'p_success':1,
                                'reward':0.01
                            },

                            {
                                'action':ClinvarDiseaseToCondition(),
                                'p_success':0.5,
                                'reward':2
                            },

                            {
                                'action':ClinvarDiseaseToGene(),
                                'p_success':0.5,
                                'reward':1
                            },

                            {
                                'action':ClinvarGeneToCondition(),
                                'p_success':0.5,
                                'reward':1
                            },

                            {
                                'action':MeshConditionToGeneticCondition(),
                                'p_success':0.5,
                                'reward':2
                            },

                            {
                                'action':MedGenConditionToGeneticCondition(),
                                'p_success':0.7,
                                'reward':1
                            }
                        ],

                    'state_vars':
                        ['bound(Disease)', 'bound(Variant)', 'bound(Gene)', 'bound(Condition)', 'bound(GeneticCondition)',
                         'connected(Variant, GeneticCondition)', 'connected(Condition, GeneticCondition)',
                         'connected(Variant, Gene)', 'connected(Disease, Variant)', 'connected(Variant, Condition)'],

                    'goal_state':['bound(GeneticCondition)', 'bound(Disease)', 'bound(Variant)',
                                  'connected(Disease, Variant)', 'connected(Variant, GeneticCondition)']
                },


                'outcome_path':{
                    'actions': 
                        [
                            {
                                'action':DrugBankDrugToTarget(),
                                'p_success':0.5,
                                'reward':3
                            },

                            {
                                'action':PharosDrugToTarget(),
                                'p_success':0.5,
                                'reward':2
                            },

                            {
                                'action':DrugBankDrugToUniProtTarget(),
                                'p_success':0.5,
                                'reward':1
                            }, 

                            {
                                'action':GoFunctionTargetToPathway(),
                                'p_success':0.5,
                                'reward':1
                            },

                            {
                                'action':WikiPWTargetToPathway(),
                                'p_success':0.5,
                                'reward':2
                            },

                            {
                                'action':WikiPWPathwayToCell(),
                                'p_success':0.3,
                                'reward':1
                            },

                            {
                                'action':PharosTargetToTissue(),
                                'p_success':0.5,
                                'reward':2
                            },

                            {
                                'action':PharosTargetToPathway(),
                                'p_success':0.5,
                                'reward':3
                            },

    #                        {
    #                            'action':PharosTargetToDisease(),
    #                            'p_success':0.5,
    #                            'reward':2
    #                        },

                            {
                                'action':PubmedPathwayDiseasePath(),
                                'p_success':0.9,
                                'reward':1
                            },

    #                        {
    #                            'action':CellOntologyTargetAndPathwayToCell(),
    #                            'p_success':0.3,
    #                            'reward':3
    #                        },

    #                        {
    #                            'action':CellOntologyTargetAndCellToPathway(),
    #                            'p_success':0.3,
    #                            'reward':3
    #                        },

                            {
                                'action':PubmedCellDiseasePath(),
                                'p_success':0.9,
                                'reward':1
                            },

                            {
                                'action':PubmedTargetDiseasePath(),
                                'p_success':0.9,
                                'reward':1
                            },

    #                        {
    #                            'action':DskdDiseaseToSymptom(),
    #                            'p_success':0.5,
    #                            'reward':2
    #                        },

                            {
                                'action':MeshScopeNoteDiseaseToSymptom(),
                                'p_success':0.5,
                                'reward':1
                            },

                            {
                                'action':PubmedDiseaseToSymptom(),
                                'p_success':0.7,
                                'reward':1
                            },

                            {
                                'action':PubmedDrugDiseasePath(),
                                'p_success':0.8,
                                'reward':0.8
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
            }

            self.state_variables = modules[module]['state_vars']
            self.actions = modules[module]['actions']
            self.default_goal = modules[module]['goal_state']
      