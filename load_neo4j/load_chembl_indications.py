import mysql.connector
import xml.etree.ElementTree as etree
from neo4j.v1 import GraphDatabase
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery
from reasoner.neo4j.Config import Config


def get_chembl_ids(session):
    result = session.run("MATCH (d:Drug) "
                         "WHERE exists(d.chembl_id) "
                         "RETURN d.chembl_id as chembl_id")
    return([record['chembl_id'] for record in result])


def add_indication(tx, chembl_id, disease_cui, disease_name):
        tx.run("MATCH (drug:Drug {chembl_id: {chembl_id}}) "
               "MATCH (disease:Disease {id: {disease_cui}}) "
               "SET disease.name = {disease_name} "
               "MERGE (drug)-[:HAS_INDICATION]->(disease)",
               chembl_id=chembl_id, disease_cui=disease_cui, disease_name=disease_name)


def get_indication(db, chembl_id):
    # prepare a cursor object using cursor() method
    cursor = db.cursor(dictionary=True)

    sql = ("SELECT di.*, md.chembl_id "
          "FROM drug_indication AS di "
          "JOIN molecule_dictionary AS md "
          "ON md.molregno = di.molregno "
          "WHERE chembl_id = %s")

    try:
        # Execute the SQL command
        data = (chembl_id,)
        cursor.execute(sql, data)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
    except:
       print("Error: unable to fetch data")

    return(results)


config = Config().config
apikey = config['umls']['apikey']
uq = UmlsQuery(apikey)
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))
db = mysql.connector.connect(user=config['chembl']['user'], password=config['chembl']['password'],
                              host=config['chembl']['host'],
                              database=config['chembl']['database'])


with driver.session() as session:
    chembl_ids = get_chembl_ids(session)

    for chembl_id in chembl_ids:
        print(chembl_id)
        results = get_indication(db, chembl_id)
        for row in results:
            for disease in uq.mesh2cui(row['mesh_id']):
                session.write_transaction(add_indication, row['chembl_id'], disease['cui'], disease['name'])

# disconnect from server
db.close()