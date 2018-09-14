import pandas as pd
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config

def get_hgnc_ids(session):
    result = session.run("MATCH (t:Target) "
                         "WHERE exists(t.hgnc_id) "
                         "RETURN DISTINCT t.hgnc_id as hgnc_id")
    return([record['hgnc_id'] for record in result])


def add_gene_ids(tx, hgnc_id, entrez_id, hgnc_symbol, approved_name):
    tx.run("MATCH (t:Target {hgnc_id: {hgnc_id}}) "
           "SET t.entrez_id = {entrez_id} "
           "SET t.hgnc_symbol = {hgnc_symbol} "
           "SET t.approved_name = {approved_name}",
        hgnc_id=hgnc_id, entrez_id=entrez_id, hgnc_symbol=hgnc_symbol, approved_name=approved_name)


genemap_file = './data/gene_mapping.txt'

genemap = pd.read_csv(genemap_file, sep="\t", dtype={'hgnc_id': object, 'ensembl_gene_id': object,
                                                     'entrez_gene_id': object, 'refseq_ids': object,
                                                     'approved_symbol': object, 'approved_name': object})


config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

with driver.session() as session:
  hgnc_ids = get_hgnc_ids(session)

genemap = genemap[genemap['hgnc_id'].isin(hgnc_ids)]
genemap = genemap.fillna('')

with driver.session() as session:
  for index, row in genemap.iterrows():
    session.write_transaction(add_gene_ids,
                              row['hgnc_id'],
                              row['entrez_gene_id'],
                              row['approved_symbol'],
                              row['approved_name'])

print("done")
