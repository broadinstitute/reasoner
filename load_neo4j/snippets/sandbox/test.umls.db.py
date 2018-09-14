import mysql.connector
from reasoner.knowledge_graph.Config import Config


def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    return(results)


# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['umls-db']['user'], password=config['umls-db']['password'],
                              host=config['umls-db']['host'],
                              database=config['umls-db']['database'])


query = 'select distinct rsab from MRSAB limit 100'
results = db_select(db, query)
print(results)
