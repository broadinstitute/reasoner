from .action import Action

class Noop(Action):
    def __init__(self):
        super().__init__([], [])

class Success(Action):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'bound(Disease)',
                         'connected(Drug, Target)', 'connected(Target, Pathway)', 'connected(Pathway, Cell)', 'connected(Cell, Symptom)', 'connected(Symptom, Disease)'], [])

class AddDrugTarget(Action):
    def __init__(self):
        super().__init__(['bound(Drug)'], ['bound(Target) and connected(Drug, Target)'])

class AddTargetPathway(Action):
    def __init__(self):
        super().__init__(['bound(Target)'], ['bound(Pathway) and connected(Target, Pathway)'])

class AddDiseaseSymptom(Action):
    def __init__(self):
        super().__init__(['bound(Disease)'], ['bound(Symptom) and connected(Symptom, Disease)'])

class AddSymptomCell(Action):
    def __init__(self):
        super().__init__(['bound(Symptom)'], ['bound(Cell) and connected(Cell, Symptom)'])

class PubmedDrugDisease(Action):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Disease)'],
                         ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom) and connected(Symptom, Disease)'])