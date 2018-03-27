import mysql.connector
import xml.etree.ElementTree as etree
from neo4j.v1 import GraphDatabase
from .Config import Config


def get_chembl_ids(session):
    result = session.run("MATCH (:Drug)-[:HAS_ID]->(id:Identifier {resource: 'ChEMBL'}) "
                "RETURN id.id as chembl_id")
    return([record['chembl_id'] for record in result])

def add_indication(tx, chembl_id, mesh_id, mesh_heading, efo_id, efo_term):
    if mesh_id is not None and efo_id is not None:
        tx.run("MATCH (drug:Drug)-[:HAS_ID]->(:Identifier {id: {chembl_id}, resource: 'ChEMBL'}) "
               "MERGE (drug)-[:HAS_INDICATION]->(condition:Condition)-[:HAS_ID]->(:Identifier {id: {mesh_id}, term: {mesh_heading}, type: 'mesh_id', resource: 'MeSH'}) "
               "MERGE (condition)-[:HAS_ID]->(:Identifier {id: {efo_id}, term: {efo_term}, type: 'efo_id', resource: 'EFO'}) "
               "MERGE (condition)-[:HAS_SYNONYM]->(:Synonym {name: {mesh_heading}, type: 'mesh_heading'}) "
               "MERGE (condition)-[:HAS_SYNONYM]->(:Synonym {name: {efo_term}, type: 'efo_term'})",
               chembl_id=chembl_id, mesh_id=mesh_id, mesh_heading=mesh_heading.lower(), efo_id=efo_id, efo_term=efo_term.lower())
    elif mesh_id is not None:
        tx.run("MATCH (drug:Drug)-[:HAS_ID]->(:Identifier {id: {chembl_id}, resource: 'ChEMBL'}) "
               "MERGE (drug)-[:HAS_INDICATION]->(condition:Condition)-[:HAS_ID]->(:Identifier {id: {mesh_id}, term: {mesh_heading}, type: 'mesh_id', resource: 'MeSH'}) "
               "MERGE (condition)-[:HAS_SYNONYM]->(:Synonym {name: {mesh_heading}, type: 'mesh_heading'})",
               chembl_id=chembl_id, mesh_id=mesh_id, mesh_heading=mesh_heading.lower())
    elif efo_id is not None:
        tx.run("MATCH (drug:Drug)-[:HAS_ID]->(:Identifier {id: {chembl_id}, resource: 'ChEMBL'}) "
           "MERGE (drug)-[:HAS_INDICATION]->(condition:Condition)-[:HAS_ID]->(:Identifier {id: {efo_id}, term: {efo_term}, type: 'efo_id', resource: 'EFO'}) "
           "MERGE (condition)-[:HAS_SYNONYM]->(:Synonym {name: {efo_term}, type: 'efo_term'})",
           chembl_id=chembl_id, efo_id=efo_id, efo_term=efo_term.lower())


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
            session.write_transaction(add_indication, row['chembl_id'], row['mesh_id'], row['mesh_heading'], row['efo_id'], row['efo_term'])

# disconnect from server
db.close()