import pandas as pd
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

drugs_file = '../data/knowledge_graph/ready_to_load/drugs.csv'

drugs = pd.read_csv(drugs_file)
kg = KnowledgeGraph()

for index, row in drugs.iterrows():
    for key, value in row.items():
        if value == '':
            row[key] = None
    kg.add_drug(row['cui'], row['chembl_id'], row['chebi_id'], row['drugbank_id'], row['name'], row['type'], row['mechanism'], row['pharmacodynamics'])
