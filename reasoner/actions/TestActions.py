from .Action import Action

class Noop(Action):
    def __init__(self):
        super().__init__([], [])
        
class Success(Action):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'bound(Disease)',
                         'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Phenotype)', 'connected(Phenotype, Disease)'], [])

class AddDrugTarget(Action):
    def __init__(self):
        super().__init__(['bound(Drug)'], ['bound(Target) and connected(Drug, Target)'])

class AddTargetPathway(Action):
    def __init__(self):
        super().__init__(['bound(Target)'], ['bound(Pathway) and connected(Target, Pathway)'])
        
class AddDiseasePhenotype(Action):
    def __init__(self):
        super().__init__(['bound(Disease)'], ['bound(Phenotype) and connected(Phenotype, Disease)'])
        
class AddPhenotypeCell(Action):
    def __init__(self):
        super().__init__(['bound(Phenotype)'], ['bound(Cell) and connected(Cell, Phenotype)'])
        
class PubmedDrugDisease(Action):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Disease)'],
                         ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Phenotype) and connected(Phenotype, Disease)'])