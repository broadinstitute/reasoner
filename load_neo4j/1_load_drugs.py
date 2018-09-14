import pandas as pd
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

drugs_file = '../data/knowledge_graph/ready_to_load/drugs.csv'

drugs = pd.read_csv(drugs_file)
kg = KnowledgeGraph()

drugs.fillna('', inplace = True)
for index, row in drugs.iterrows():
    kg.add_drug(row['cui'], row['chembl_id'], row['chebi_id'], row['drugbank_id'], row['name'], row['type'], row['mechanism'], row['pharmacodynamics'])
