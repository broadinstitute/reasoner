import pandas
from reasoner.KGAgent import KGAgent

cop_file = '../data/neo4j/cop_benchmark_input_cui_curated.csv'
cop = pandas.read_csv(cop_file)

agent = KGAgent()
for index, row in cop.iterrows():
    agent.cop_query(row['drug_cui'], row['disease_cui'])
