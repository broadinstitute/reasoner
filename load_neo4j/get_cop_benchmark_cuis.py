import pandas
import csv
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

cop_file = '../data/neo4j/cop_benchmark.csv'
outfile = '../data/neo4j/cop_benchmark_input_cui.csv'

cop = pandas.read_csv(cop_file)

uq = UmlsQuery()
drug_disease_pairs = [['drug_name', 'drug_cui', 'disease_name', 'disease_cui']]
for index, row in cop.iterrows():
	drug_result = uq.mesh2cui(row['Drug_MeSH_ID'])
    if drug_result:
        disease_result = uq.mesh2cui(row['Disease_MeSH_ID'])
        if disease_result:
            drug_disease_pairs.append([drug_result[0]['name'], drug_result[0]['cui'],disease_result[0]['name'], disease_result[0]['cui']])

with open(outfile, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(drug_disease_pairs)
