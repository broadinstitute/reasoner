import pandas as pd
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

pathway_file = '../data/knowledge_graph/ready_to_load/pathways.csv'
protein2pathway_file = '../data/knowledge_graph/ready_to_load/protein_to_pathways.csv'

kg = KnowledgeGraph()
pathways = pd.read_csv(pathway_file)
pathways.fillna('', inplace = True)
for index, row in pathways.iterrows():
        kg.add_pathway(row['go_id'], row['name'], row['cui'])


protein2pathway = pd.read_csv(protein2pathway_file)
protein2pathway.fillna('', inplace = True)
for index, row in protein2pathway.iterrows():
    if row['db'] == 'UniProtKB':
        kg.add_protein_pathway_relation(row['db_object_id'], row['go_id'], row['evidence_code'])
