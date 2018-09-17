import pandas as pd
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

disease_file = '../data/knowledge_graph/ready_to_load/diseases.csv'
disease = pd.read_csv(disease_file)

kg = KnowledgeGraph()
for index, row in disease.iterrows():
    if row['hpo_id'] == '':
        kg.add_disease(row['cui'], row['name'], row['mesh_id'])
    else:
        kg.add_disease(row['cui'], row['name'], row['mesh_id'], row['hpo_id'])
