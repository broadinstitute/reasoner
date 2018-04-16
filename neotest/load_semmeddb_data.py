import pandas as pd
import mysql.connector
from neo4j.v1 import GraphDatabase
from Config import Config


def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    
    return(results)


def get_cuis(session, node_type):
    result = session.run("MATCH (n:%s) RETURN DISTINCT n.id as cui" % (node_type))
    return([record['cui'] for record in result])


def add_cui_connection(tx, origin_cui, origin_type, origin_name, target_cui, target_type, target_name, predicate, pred_count):
    tx.run("MERGE (o:%s {id: {origin_cui}}) "
           "SET o.name = {origin_name} "
           "MERGE (t:%s {id: {target_cui}}) "
           "SET t.name = {target_name} "
           "MERGE (o)-[r:%s]->(t) "
           "SET r.count = {pred_count}" % (origin_type, target_type, predicate),
           origin_cui=origin_cui, origin_name=origin_name, target_cui=target_cui, target_name=target_name, pred_count=pred_count)
    print("added connection: " + origin_cui + "," + predicate + "," + target_cui)


def sql2neo(session, db, origin, target, origin_role = 'subject', target_id_type = 'type'):
    type2sem = {'Disease': ['dsyn'],
               'Symptom': ['sosy'],
               'Tissue': ['tisu', 'bpoc', 'blor'],
               'Cell': ['cell'],
               'Pathway': ['moft', 'celf']}

    sem2type = {'dsyn': 'Disease',
                'sosy': 'Symptom',
                'tisu': 'Tissue',
                'bpoc': 'Tissue',
                'blor': 'Tissue',
                'cell': 'Cell',
                'moft': 'Pathway',
                'celf': 'Pathway'}

    ## prepare sql template
    sql_template = "SELECT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE, COUNT(*) as COUNT FROM PREDICATION "
    
    # set origin
    if from_role == 'object':
        sql_template = sql_template + "WHERE OBJECT_CUI = '%s' AND SUBJECT_" % (origin,)
    else:
        sql_template = sql_template + "WHERE SUBJECT_CUI = '%s' AND OBJECT_" % (origin,)

    # set target
    if target_id_type == 'cui':
        sql_template = base_sql + "CUI = '%s' " % (target,)
    else:
        sql_template = sql_template + "SEMTYPE IN ('%s') " % ("','".join(type2sem[target])),)

    sql = sql_template + "GROUP BY (SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE) LIMIT 100;"

    ## get results
    results = db_select(db, sql)
    return_cuis = set()
    for row in results:
        if row['SUBJECT_SEMTYPE'] in typemap and row['OBJECT_SEMTYPE'] in typemap:
            session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], sem2type[row['SUBJECT_SEMTYPE']],
                                      row['SUBJECT_NAME'], row['OBJECT_CUI'], sem2type[row['OBJECT_SEMTYPE']],
                                      row['OBJECT_NAME'], row['PREDICATE'], row['COUNT'])
        else:
            print("type not found: ", row['SUBJECT_SEMTYPE'], row['OBJECT_SEMTYPE'])

        if from_role == 'object':
            return_cuis.add(row['OBJECT_CUI'])
        else:
            return_cuis.add(row['SUBJECT_CUI'])

    return(return_cuis)


# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['semmeddb']['user'], password=config['semmeddb']['password'],
                              host=config['semmeddb']['host'],
                              database=config['semmeddb']['database'])

driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


with driver.session() as session:

    print('disease:')
    for index, row in get_cuis(session, 'Disease'):
        sql2neo(session, db, row['cui'], 'Symptom')
        sql2neo(session, db, row['cui'], 'Tissue')
        sql2neo(session, db, cui, 'Tissue', origin_role = 'object')
        sql2neo(session, db, row['cui'], 'Cell')
        sql2neo(session, db, row['cui'], 'Cell', origin_role = 'object')
        sql2neo(session, db, row['cui'], 'Pathway')

    print('pathway:')
    for index, row in get_cuis(session, 'Pathway'):
        sql2neo(session, db, row['cui'], 'Cell')
        sql2neo(session, db, row['cui'], 'Disease')
        
    print('symptom:')
    for symptom_cui in get_cuis(session, 'Symptom'):
        sql2neo(session, db, symptom_cui, 'Tissue')
    
    print('tissue:')
    for tissue_cui in get_cuis(session, 'Tissue'):
        sql2neo(session, db, tissue_cui, 'Cell')

    print('cell:')
    for cell_cui in get_cuis(session, 'Cell'):
        sql2neo(session, db, cell_cui, 'Tissue')
        sql2neo(session, db, cell_cui, 'Pathway')




# disconnect from server
db.close()
