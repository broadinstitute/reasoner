from .action import Action
import pandas as pd


class FileSourcedAction(Action):

    def __init__(self, precondition_entities, effect_entities, source_file, column_map):
        assert len(column_map) == 1, 'FileSourcedAction only supports single effect'
        super().__init__(precondition_entities,effect_entities)
        self.precondition_entity_list = [self.parse_input_entity(entity) for entity in precondition_entities]
        self.source_file = source_file
        self.column_map = column_map
        self.precondition_columns = self.precondition_column_map(self.precondition_entity_list)
        print(self.precondition_columns)
        assert len(self.precondition_columns) == len(self.precondition_entity_list), \
          'precondition_entities '+str(self.precondition_entity_list)+' not found among column_map values '+str(column_map)

    def parse_input_entity(self, precondition_entity):
        assert precondition_entity[0:6]=='bound(' and precondition_entity[-1]==')', \
          'Wrong input entity spec: '+ precondition_entity
        return precondition_entity[6:-1]

    def precondition_column_map(self, precondition_entities):
        map = {}
        for spec in self.column_map:
            print(spec)
            for column in self.column_map[spec]:
                if self.column_map[spec][column].get('precondition') in precondition_entities:
                    map[self.column_map[spec][column].get('precondition')] = column
        return map


    def row_to_entry(self, row):
        entries = {}
        for spec in self.column_map:
            entry = {'node':{},'edge':{}}
            for column in self.column_map[spec]:
                key_dict = self.column_map[spec][column]
                for key in key_dict:
                    if key == 'node_value':
                        for value_key in key_dict[key]:
                            entry['node'][value_key] = key_dict[key][value_key]
                    if key == 'edge_value':
                        for value_key in key_dict[key]:
                            entry['edge'][value_key] = key_dict[key][value_key]
                    if key == 'node' or key == 'edge':
                        entry[key][key_dict[key]] = row[column]
            entries[spec] = [entry]
        return entries


    def execute(self, input):
        res = []
        df = self.read_file()
        for index, row in df.iterrows():
            if self.match(row, input):
                res.append(self.row_to_entry(row))
        return res


    def match(self, row, input):
        for key in input:
            if row[self.precondition_columns[key]].lower() != input[key].lower():
                return False
        return True


    def read_file(self):
        df = pd.read_csv(self.source_file,sep='\t',keep_default_na=False)
        print('Read '+str(len(df))+' lines: '+self.source_file)
        return df


class CashedFileSourcedAction(FileSourcedAction):

    def __init__(self, precondition_entities, effect_entities, source_file, column_map):
        super().__init__(precondition_entities,effect_entities, source_file, column_map)
        self.input = self.parse_input_file(self.read_file())


    def parse_input_file(self, input):
        input_map = {}
        for index, row in input.iterrows():
            map = input_map
            for entity in self.precondition_entity_list:
                key = row[self.precondition_columns[entity]].lower()
                if key not in map:
                    map[key]={}
                map = map[key]
            if 'list' not in map:
                map['list']=[]
            map['list'].append(self.row_to_entry(row))
        return input_map


    def execute(self, input):
        map = self.input
        for entity in self.precondition_entity_list:
            if input[entity].lower() not in map:
                return []
            map=map[input[entity].lower()]
        return map['list']


class DrugBankDrugToTarget(CashedFileSourcedAction):

    def __init__(self, filename='./data/drugbank.txt'):
        column_map = { 'Target': {
            'Name': {'precondition':'Drug'},
            'Action': {'edge':'action'},
            'TargetID': {'node':'id'},
            'Symbol': {'node':'name'},
            'HGNC': {'node':'HGNC'},
            '+1': {'node_value': {'authority':'DrugBank:TargetID'}}
        }}
        super().__init__(['bound(Drug)'],['bound(Target) and connected(Drug, Target)'], filename, column_map)


class GoFunctionTargetToPathway(CashedFileSourcedAction):

    def __init__(self, filename='./data/GO_function.txt'):
        column_map = { 'Pathway': {
            'Symbol': {'precondition':'Target'},
            'GOID': {'node':'id'},
            'GOTerm': {'node':'name'},
            'GOEvidenceCode': {'edge':'GOEvidenceCode'},
            '+1': {'node_value': {'authority':'GO'}}
        }}
        super().__init__(['bound(Target)'],['bound(Pathway) and connected(Target, Pathway)'], filename, column_map)


class MeshScopeNoteDiseaseToPhenotype(CashedFileSourcedAction):
    def __init__(self, filename='./data/MeshScopeNote.txt'):
        column_map = { 'Phenotype': {
            'MeSH_term': {'precondition':'Disease'},
            'scopeNote_term': {'node':'scopeNote'},
            'scopeNote_MeshTerm': {'node':'name'}
        }}
        super().__init__(['bound(Disease)'],['bound(Phenotype) and connected(Disease, Phenotype)'], filename, column_map)


class CellOntologyTargetToPathway(CashedFileSourcedAction):

    def __init__(self, filename='./data/cellOntology2GO.txt'):
        column_map = {'Pathway':{
            'Symbol': {'precondition': 'Target'},
            'name': {'precondition': 'Cell'},
            'qualifier': {'edge': 'qualifier'},
            'GOID': {'node':'id'},
            'GOTerm': {'node':'name'},
            '+1': {'node_value': {'authority':'GO'}}
        }}
        super().__init__(['bound(Target)','bound(Cell)'],['bound(Pathway) and connected(Pathway, Target) and connected(Pathway, Cell)'], filename, column_map)


