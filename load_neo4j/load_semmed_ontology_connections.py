import mysql.connector
from neo4j.v1 import GraphDatabase
from reasoner.neo4j.Config import Config

def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    try:
       cursor.execute(sql)
       results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    cursor.execute(sql)
    results = cursor.fetchall()
    return(results)

def add_cui_connection(tx, origin_cui, origin_type, target_cui, target_name, predicate, pred_count):
    tx.run("MERGE (o:%s {cui: {origin_cui}}) "
           "MERGE (t {cui: {target_cui}}) "
           "SET t.name = {target_name} "
           "MERGE (o)-[r:%s {source: 'semmeddb_iter2'}]->(t) "
           "SET r.count = {pred_count}" % (origin_type, predicate),
           origin_cui=origin_cui, target_cui=target_cui, target_name=target_name, pred_count=pred_count)

def get_cuis(session):
    result = session.run("MATCH (n) "
                         "WHERE exists(n.cui) "
                         "RETURN n.cui as cui, labels(n) as labels")
    return({record['cui']: record['labels'][0] for record in result})


# def get_connections(db, subject_cui, object_cui):
#   sql = ("SELECT predicate, COUNT(*) as count "
#          "FROM PREDICATION "
#          "WHERE subject_cui = '%s' " 
#          "AND object_cui = '%s' "
#          "GROUP BY predicate "
#          "HAVING COUNT(*) > 10;") % (subject_cui, object_cui)
#     return(db_select(db, sql))


def get_connections(db, subject_cui):
    sql = ("SELECT predicate, object_cui, object_semtype, object_name, COUNT(*) as count "
           "FROM PREDICATION "
           "WHERE subject_cui = '%s' " 
           "GROUP BY predicate, object_cui, object_semtype "
           "HAVING COUNT(*) > 10;") % (subject_cui)
    return(db_select(db, sql))

def load_connections(session, subject_cui, subject_type, connections):
    for connection in connections:
        print(subject_cui, subject_type, connection['object_cui'],
              connection['predicate'], connection['count'])
        session.write_transaction(add_cui_connection, subject_cui, subject_type,
                                      connection['object_cui'], connection['object_name'],
                                      connection['predicate'], connection['count'])

# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['semmeddb']['user'], password=config['semmeddb']['password'],
                              host=config['semmeddb']['host'],
                              database=config['semmeddb']['database'])

driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


with driver.session() as session:
    nodes = get_cuis(session)
    for subject_cui, subject_type in nodes.items():
        results = get_connections(db, subject_cui)
        load_connections(session, subject_cui, subject_type, results)
