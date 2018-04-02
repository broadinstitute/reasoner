import pandas as pd
import mysql.connector
from neo4j.v1 import GraphDatabase
from Config import Config


def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    return(results)


# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['semmeddb']['user'], password=config['semmeddb']['password'],
                              host=config['semmeddb']['host'],
                              database=config['semmeddb']['database'])

sql = ("select distinct cui1 as location_cui, RELA as relation, "
       "cui2 as disease_cui, A.str as location_str, B.str as disease_str, MRREL.sab as source "
       "from MRREL "
       "inner join MRSTY "
       "on MRREL.cui2 = MRSTY.cui "
       "left join MRCONSO A on A.cui = MRREL.cui1 "
       "left join MRCONSO B on B.cui = MRREL.cui2 "
       "where tui = 'T047' "
       "and RELA = 'has_finding_site' "
       "and A.ispref = 'Y' "
       "and A.TS = 'P' "
       "and A.lat='ENG' "
       "and A.stt = 'PF' "
       "and B.ispref = 'Y' "
       "and B.TS = 'P' "
       "and B.lat='ENG' "
       "and B.stt = 'PF' "
       "limit 10;")

result = db_select(db, sql)
print(result)