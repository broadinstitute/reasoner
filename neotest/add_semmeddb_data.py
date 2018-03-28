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


def add_cui_connection(tx, origin_cui, origin_type, target_cui, target_type, target_name, predicate):
    tx.run("MERGE (o:%s)-[:HAS_ID]->(:Identifier {id: {origin_cui}}) "
           "MERGE (t:%s)-[:HAS_ID]->(:Identifier {id: {target_cui}}) "
           "SET t.id = {target_cui} "
           "SET t.name = {target_name} "
           "MERGE (o)-[:%s]->(t) "
           "MERGE (t)-[:HAS_ID]->(:Identifier {id: {target_cui}, type: 'cui', resource: 'UMLS'}) "
           "MERGE (t)-[:HAS_SYNONYM]->(:Synonym {name: {target_name}, type: 'umls_concept'})" % (origin_type, target_type, predicate),
           origin_cui=origin_cui, target_cui=target_cui, target_name=target_name)
    print("added connection: " + origin_cui + "," + predicate + "," + target_cui)

def sql2neo(session, db, subject_cui, subject_type, object_type):
    typemap = {'Disease': 'dsyn',
               'Symptom': 'sosy',
               'Tissue': 'tisu',
               'Cell': 'cell',
               'Pathway': ['moft', 'celf']}

    if object_type == 'Pathway':
        sql = ("SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE "
           "FROM PREDICATION "
           "WHERE SUBJECT_CUI = '%s' "
           "AND OBJECT_SEMTYPE IN ('%s') LIMIT 100;") % (subject_cui, "','".join(typemap[object_type]))
    else:
        sql = ("SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE "
               "FROM PREDICATION "
               "WHERE SUBJECT_CUI = '%s' "
               "AND OBJECT_SEMTYPE = '%s' LIMIT 100;") % (subject_cui, typemap[object_type])
    results = db_select(db, sql)
    return_cuis = set()
    for row in results:
        return_cuis.add(row['OBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], subject_type, row['OBJECT_CUI'], object_type, row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

def sql2neo_object(session, db, object_cui, object_type, subject_type):
    typemap = {'Disease': 'dsyn',
               'Symptom': 'sosy',
               'Tissue': 'tisu',
               'Cell': 'cell',
               'Pathway': ['moft', 'celf']}

    if subject_type == 'Pathway':
        sql = ("SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE "
           "FROM PREDICATION "
           "WHERE OBJECT_CUI = '%s' "
           "AND SUBJECT_SEMTYPE IN ('%s') LIMIT 100;") % (object_cui, "','".join(typemap[subject_type]))
    else:
        sql = ("SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE "
               "FROM PREDICATION "
               "WHERE OBJECT_CUI = '%s' "
               "AND SUBJECT_SEMTYPE = '%s' LIMIT 100;") % (object_cui, typemap[subject_type])
    results = db_select(db, sql)
    return_cuis = set()
    for row in results:
        return_cuis.add(row['SUBJECT_CUI'])
        session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], subject_type, row['OBJECT_CUI'], object_type, row['OBJECT_NAME'], row['PREDICATE'])
    return(return_cuis)

def sql2neo_direct(session, db, subject_cui, object_cui):
    typemap = {'dsyn': 'Disease',
               'moft': 'Pathway',
               'celf': 'Pathway',
               'neop': 'Pathway'}

    sql = ("SELECT DISTINCT SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, PREDICATE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE "
       "FROM PREDICATION "
       "WHERE SUBJECT_CUI = '%s' "
       "AND OBJECT_CUI = '%s' LIMIT 100;") % (subject_cui, object_cui)
    results = db_select(db, sql)
    return_cuis = set()
    for row in results:
        if row['SUBJECT_SEMTYPE'] in typemap and row['OBJECT_SEMTYPE']:
          session.write_transaction(add_cui_connection, row['SUBJECT_CUI'], typemap[row['SUBJECT_SEMTYPE']], row['OBJECT_CUI'], typemap[row['OBJECT_SEMTYPE']], row['OBJECT_NAME'], row['PREDICATE'])
        else:
          print(row['SUBJECT_SEMTYPE'], row['OBJECT_SEMTYPE'])


def disease2symptoms(session, db, cui):
    return(sql2neo(session, db, cui, 'Disease', 'Symptom'))

#def disease2pathway(session, db, cui):
#    return(sql2neo(session, db, cui, 'Disease', 'Pathway'))

def disease2tissue(session, db, cui):
    return(sql2neo_object(session, db, cui, 'Disease', 'Tissue'))

def disease2cell(session, db, cui):
    return(sql2neo(session, db, cui, 'Disease', 'Cell')|sql2neo_object(session, db, cui, 'Disease', 'Cell'))



def symptom2tissue(session, db, cui):
    return(sql2neo(session, db, cui, 'Symptom', 'Tissue'))

def tissue2cell(session, db, cui):
    return(sql2neo(session, db, cui, 'Tissue', 'Cell'))

def pathway2cell(session, db, cui):
    return(sql2neo(session, db, cui, 'Pathway', 'Cell'))

def cell2tissue(session, db, cui):
    return(sql2neo(session, db, cui, 'Cell', 'Tissue'))


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
    symptom_cuis = set()
    tissue_cuis = set()
    cell_cuis = set()

    print('disease:')
    for index, row in disease.iterrows():
        symptom_cuis = symptom_cuis|disease2symptoms(session, db, row['cui'])
        tissue_cuis = tissue_cuis|disease2tissue(session, db, row['cui'])
        cell_cuis = cell_cuis|disease2cell(session, db, row['cui'])
        # for p_index, p_row in pathway.iterrows():
        #     sql2neo_direct(session, db, row['cui'], p_row['cui'])
        #     sql2neo_direct(session, db, p_row['cui'], row['cui'])

    print('pathway:')
    for index, row in pathway.iterrows():
        cell_cuis = cell_cuis|pathway2cell(session, db, row['cui'])
        
    print('symptom:')
    for symptom_cui in symptom_cuis:
        tissue_cuis = tissue_cuis|symptom2tissue(session, db, symptom_cui)
    
    print('tissue:')
    for tissue_cui in tissue_cuis:
        cell_cuis = cell_cuis|tissue2cell(session, db, tissue_cui)

    print('cell:')
    for tissue_cui in tissue_cuis:
        cell_cuis = cell_cuis|tissue2cell(session, db, tissue_cui)




# disconnect from server
db.close()
