import mysql.connector
from .Config import Config

def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
       print("Error: unable to fetch data")
    return(results)


def add_cui_connection(tx, origin_cui, origin_type, target_cui, target_type, target_name, predicate):
    tx.run("MATCH (o:{origin_type})-[:HAS_ID]->(:Identifier {id: {origin_cui}}) "
           "MERGE (o)-[:{predicate}]->(t:{target_type} {id: {target_cui}, name: {target_name}}) "
           "MERGE (t)-[:HAS_ID]->(:Identifier {id: {target_cui}, type: 'cui', resource: 'UMLS'}) "
           "MERGE (t)-[:HAS_SYNONYM]->(:Synonym {name: {target_name}, type: 'umls_concept'})",
           origin_cui=origin_cui, origin_type=origin_type, target_cui=target_cui, target_type=target_type, target_name=target_name, predicate=predicate)


def disease2symptoms(session, db, disease_cui):
    sql = "SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE FROM PREDICATION WHERE SUBJECT_CUI = '%s' AND SUBJECT_SEMTYPE = 'dsyn' AND OBJECT_SEMTYPE = 'sosy' AND PREDICATE = 'CAUSES' LIMIT 100;"
    results = db_select(sql)
    return_cuis = []
    for row in results:
        return_cuis.append(row['OBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], 'Disease', row['OBJECT_CUI'], 'Symptom', row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

def symptom2tissue(session, db, symptom_cui):
    sql = "SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE FROM PREDICATION WHERE SUBJECT_CUI = '%s' AND SUBJECT_SEMTYPE = 'tisu' AND OBJECT_SEMTYPE = 'sosy' AND PREDICATE = 'LOCATION_OF' LIMIT 100;"
    results = db_select(sql)
    return_cuis = []
    for row in results:
        return_cuis.append(row['OBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], 'Symptom', row['OBJECT_CUI'], 'Tissue', row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

def tissue2cell(session, db, tissue_cui):
    sql = "SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE FROM PREDICATION WHERE SUBJECT_CUI = '%s' AND SUBJECT_SEMTYPE = 'cell' AND OBJECT_SEMTYPE = 'tisu' AND PREDICATE = 'PART_OF' LIMIT 100;"
    results = db_select(sql)
    return_cuis = []
    for row in results:
        return_cuis.append(row['OBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], 'Tissue', row['OBJECT_CUI'], 'Cell', row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

def pathway2cell(session, db, pathway_cui):
    sql = "SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE FROM PREDICATION WHERE SUBJECT_CUI = '%s' AND (SUBJECT_SEMTYPE = 'celf' OR SUBJECT_SEMTYPE = 'moft') AND OBJECT_SEMTYPE = 'cell' AND PREDICATE = 'AFFECTS' LIMIT 100;"
    results = db_select(sql)
    return_cuis = []
    for row in results:
        return_cuis.append(row['OBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], 'Pathway', row['OBJECT_CUI'], 'Cell', row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

#SELECT DISTINCT PREDICATE FROM PREDICATION WHERE SUBJECT_SEMTYPE = 'cell' AND OBJECT_SEMTYPE = 'tisu' LIMIT 10;
#SELECT DISTINCT PREDICATE FROM PREDICATION WHERE (SUBJECT_SEMTYPE = 'celf' OR SUBJECT_SEMTYPE = 'moft') AND OBJECT_SEMTYPE = 'cell' LIMIT 10;
#SELECT DISTINCT PREDICATE FROM PREDICATION WHERE SUBJECT_SEMTYPE = 'cell' AND (OBJECT_SEMTYPE = 'celf' OR OBJECT_SEMTYPE = 'moft') LIMIT 10;



# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['semmeddb']['user'], password=config['semmeddb']['password'],
                              host=config['semmeddb']['host'],
                              database=config['semmeddb']['database'])

driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

disease_file = './data/cop_disease_cui.csv'
pathway_file = './data/cop_pathway_cui.csv'

disease = pd.read_csv(disease_file)
pathway = pd.read_csv(pathway_file)

with driver.session() as session:
    for index, row in disease.iterrows():
        print(row)
        symptom_cuis = disease2symptoms(session, db, row['cui'])
        for symptom_cui in symptom_cuis:
            tissue_cuis = symptom2tissue(session, db, symptom_cui)
            for tissue_cui in tissue_cuis:
                cell_cuis = tissue2cell(session, db, tissue_cui)

    for index, row in pathway.iterrows():
        pathway2cell(session, db, row['cui'])


# disconnect from server
db.close()