from neo4j.v1 import GraphDatabase
from reasoner.neo4j.Config import Config

def get_chebi_terms(session):
    result = session.run("MATCH (term:ChebiTerm) "
           "WHERE not term:Drug "
           "RETURN term.chebi_id as chebi_id;")
    return(result)

outfile = '../data/neo4j/all_chebi_terms.txt'

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


with driver.session() as session:
    chebi_terms = [record['chebi_id'] for record in get_chebi_terms(session)]

with open(outfile,'w') as f:
    for term in chebi_terms:
        f.write("%s\n" % term)
