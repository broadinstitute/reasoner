from .action import Action

class EditGeneticConditionToDisease(Action):
    def __init__(self):
        super().__init__(['bound(GeneticCondition)'],['bound(Disease)'])
        
    def execute(self, query):
        return [{'Disease':[{'node':{'name':query['GeneticCondition']}, 'edge':{}}]}]