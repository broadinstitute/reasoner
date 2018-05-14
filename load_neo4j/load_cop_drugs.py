import pandas
from reasoner.knowledge_graph.ChemblTools import ChemblTools
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

cop_drugs_file = '../data/neo4j/cop_chembl_ids_curated.csv'
cop_drugs = pandas.read_csv(cop_drugs_file)

ct = ChemblTools()
kg = KnowledgeGraph()

for index, row in cop_drugs.iterrows():
    cui = row['cui']
    if not pandas.isnull(row['chembl_id']):
        chembl_id = row['chembl_id']
    else:
        chembl_id = None
    if not pandas.isnull(row['chebi_id']):
        chebi_id = row['chebi_id']
    else:
        chebi_id = None
    if not pandas.isnull(row['drugbank_id']):
        drugbank_id = row['drugbank_id']
    else:
        drugbank_id = None
    # print(cui, chembl_id, chebi_id, drugbank_id)
    kg.add_drug(cui, chembl_id, chebi_id, drugbank_id)
    
    # add targets
    if chembl_id is not None:
        targets = ct.get_targets(chembl_id)
    for target in targets:
        if target['db_source'] in['SWISS-PROT', 'TREMBL']:
            # print(target['chembl_id'], target['accession'], target['target_name'],
            #       target['standard_value'], target['standard_type'], target['standard_units'],
            #       target['standard_flag'], target['typeyear'])
            kg.add_chembl_target(target['chembl_id'], target['accession'], target['target_name'],
                  target['standard_value'], target['standard_type'], target['standard_units'])
    
    # kg.add_chebi_terms(self)
