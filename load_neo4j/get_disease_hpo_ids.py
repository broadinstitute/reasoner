import pandas as pd
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

disease_file = '../data/neo4j/graph/diseases.csv'
diseases = pd.read_csv(disease_file)

uq = UmlsQuery()

ndis = diseases.shape()[0]
hpo_ids = ['']*ndis
for index, row in diseases.iterrows():
	result = uq.cui2hpo(row['cui'])
    if result:
        hpo_ids[index] = result[0]['hpo_id']



