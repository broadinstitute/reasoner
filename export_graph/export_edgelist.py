import csv
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

np.random.seed(439572)

outfile = 'data/knowledge_graph/export/edgelist.txt'

kg = KnowledgeGraph()
result = kg.get_edgelist()

edgelist = []
for record in result:
    edgelist.append([record['start'], record['end']])

with open(outfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(edgelist)