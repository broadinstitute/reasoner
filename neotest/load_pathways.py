from neo4j.v1 import GraphDatabase
from Config import Config

def add_pathway(tx, name, url, entrez_ids):
    tx.run("MERGE (pathway:Pathway {name: {name}, url: {url}}) "
    	   "WITH pathway "
    	   "UNWIND {entrez_ids} as entrez_id "
    	   "MATCH (item:Target)-[:HAS_ID]->(identifier:Identifier {id: entrez_id, type: 'entrez_gene_id'}) "
    	   "MERGE (item)-[:PART_OF]->(pathway)",
    	name=name, url=url, entrez_ids=entrez_ids)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

msigdb_file = './data/c2cp_c5mf_c5bp_v6.1.entrez.gmt'

pathways = []
with open(msigdb_file) as f:
	for line in f:
		parts = line.strip().split('\t')
		pathways.append({'name':parts[0], 'url':parts[1], 'entrez_ids':parts[2:]})

with driver.session() as session:
	for pathway in pathways:
		session.write_transaction(add_pathway, pathway['name'], pathway['url'], pathway['entrez_ids'])

print('done')