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
    return(results)


def set_semtype(tx, cui, semtype):
    tx.run("MATCH (term {cui: {cui}}) "
           "SET term:%s" % (semtype),
           cui=cui)


def get_cuis(session):
    result = session.run("MATCH (n) "
                         "WHERE exists(n.cui) "
                         "RETURN n.cui as cui")
    return([record['cui'] for record in result])


def get_semtype(db, cui):
    sql = ("SELECT tui type_id, abr type_name "
           "FROM MRSTY "
           "LEFT JOIN SRDEF on SRDEF.ui=MRSTY.tui "
           "WHERE cui = '%s';") % (cui)
    return(db_select(db, sql))


# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['umls-db']['user'], password=config['umls-db']['password'],
                              host=config['umls-db']['host'],
                              database=config['umls-db']['database'])

driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


with driver.session() as session:
    cuis = get_cuis(session)
    for cui in cuis:
        semtypes = get_semtype(db, cui)
        for record in semtypes:
            session.write_transaction(set_semtype, cui, record['type_name'].decode())
