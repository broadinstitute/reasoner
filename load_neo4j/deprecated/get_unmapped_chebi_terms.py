import csv
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery


def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    return(results)


def get_chebi_terms(session):
    result = session.run("MATCH ()-[:HAS_ROLE]-(c:ChebiTerm) "
                         "WHERE NOT c:Drug "
                         "AND NOT exists(c.cui) "
                         "RETURN DISTINCT c.name as name, c.chebi_id as chebi_id;")
    return(result)


outfile = '../data/neo4j/chebi2umls_by_name.csv'

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


with driver.session() as session:
    chebi_terms = get_chebi_terms(session)

mappings = [['chebi_id', 'chebi_name', 'cui', 'umls_name']]
uq = UmlsQuery()
for term in chebi_terms:
    umls_result = uq.search(term['name'])
    print(term)
    if umls_result:
        mappings.append([term['chebi_id'], term['name'], umls_result['results'][0]['ui'], umls_result['results'][0]['name']])

with open(outfile, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(mappings)