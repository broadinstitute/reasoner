import os
import csv
import re
import numpy as np
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

np.random.seed(439572)

def get_preferred_label(labels):
    if 'Drug' in labels:
        return('Drug')
    elif 'Disease' in labels:
        return('Disease')
    else:
        return("ChebiTerm")


outfolder = 'translator_test_1'

kg = KnowledgeGraph()

result = kg.query("""
         MATCH path = (dr:Drug)-[:HAS_ROLE]->(t:ChebiTerm)--(dis:Disease)--(dr)
         UNWIND relationships(path) as r
         RETURN startNode(r) as start, r, endNode(r) as end
         """)

graph_triples = []
target_triples = []
for record in result:
    start_term = get_preferred_label(record['start'].labels) + '_' + re.sub(r'[ ,\'-]', "",record['start']['name'])
    end_term = get_preferred_label(record['end'].labels) + '_' + re.sub(r'[ ,\'-]', "",record['end']['name'])
    relation = record['r'].type
    if relation == 'HAS_INDICATION':
        target_triples.append([start_term, relation, end_term])
    else:
        graph_triples.append([start_term, relation, end_term])

# split target triples into training and test set
n_targets = len(target_triples)
randidx = np.random.permutation(n_targets)
training_idx, test_idx = randidx[:np.floor(n_targets/2).astype(int)], randidx[np.floor(n_targets/2).astype(int):]
train_triples = [target_triples[i] for i in training_idx]
test_triples = [target_triples[i] for i in test_idx]
dev_triples = train_triples[1:50]

os.mkdir(outfolder)
graphfile = os.path.join(outfolder, 'graph.txt')
trainfile = os.path.join(outfolder, 'train.txt')
testfile = os.path.join(outfolder, 'test.txt')
devfile = os.path.join(outfolder, 'dev.txt')

with open(graphfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(graph_triples + train_triples)

with open(trainfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(train_triples)

with open(testfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(test_triples)

with open(devfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(dev_triples)
