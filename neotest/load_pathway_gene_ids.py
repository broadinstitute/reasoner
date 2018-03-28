import pandas as pd
from neo4j.v1 import GraphDatabase
from Config import Config

def get_hgnc_ids(session):
    result = session.run("MATCH ()-[:HAS_ID]->(id:Identifier) "
                         "WHERE id.id STARTS WITH 'HGNC:' "
                         "RETURN DISTINCT id.id as hgnc_id")
    return([record['hgnc_id'] for record in result])


def add_gene_ids(tx, hgnc_id, ensembl_id, entrez_id,
                 refseq_id, hgnc_symbol, approved_name):
    tx.run("MATCH (item)-[:HAS_ID]->(:Identifier {id: {hgnc_id}}) "
           "MERGE (item)-[:HAS_ID]->(:Identifier {id: {ensembl_id}, type: 'ensembl_gene_id', resource: 'Ensembl'}) "
           "MERGE (item)-[:HAS_ID]->(:Identifier {id: {entrez_id}, type: 'entrez_gene_id', resource: 'Entrez'}) "
           "MERGE (item)-[:HAS_ID]->(:Identifier {id: {refseq_id}, type: 'refseq_id', resource: 'RefSeq'}) "
           "MERGE (item)-[:HAS_SYNONYM]->(:Synonym {name: {hgnc_symbol}, type: 'hgnc_symbol'}) "
           "MERGE (item)-[:HAS_SYNONYM]->(:Synonym {name: {approved_name}, type: 'approved_name'})",
        hgnc_id=hgnc_id, ensembl_id=ensembl_id, entrez_id=entrez_id, refseq_id=refseq_id, hgnc_symbol=hgnc_symbol, approved_name=approved_name)


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
                              row['ensembl_gene_id'],
                              row['entrez_gene_id'],
                              row['refseq_ids'],
                              row['approved_symbol'],
                              row['approved_name'])

print("done")
