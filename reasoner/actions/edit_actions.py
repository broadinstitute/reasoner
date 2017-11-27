"""Actions used by the agent to apply internal knowledge.
"""

from .action import Action

class EditGeneticConditionToDisease(Action):
    """Change the entity from GeneticCondition to Disease.
    """
    def __init__(self):
        super().__init__(['bound(GeneticCondition)'],['bound(Disease)'])
        
    def execute(self, query):
        return [{'Disease':[{'node':{'name':query['GeneticCondition']}, 'edge':{}}]}]