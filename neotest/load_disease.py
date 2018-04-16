import pandas as pd
from neo4j.v1 import GraphDatabase
from Config import Config


def add_disease(tx, cui, name, mesh_id):
    tx.run("MERGE (disease:Disease {id: {cui}}) "
           "SET disease.name =  {name} "
           "SET disease.mesh_id = {mesh_id}",
           cui=cui, name=name, mesh_id=mesh_id)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

disease_file = './data/cop_disease_cui.csv'
disease = pd.read_csv(disease_file)

with driver.session() as session:
    for index, row in disease.iterrows():
        print(row)
        session.write_transaction(add_disease, row['cui'], row['name'], row['mesh_id'])
