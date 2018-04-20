import pandas as pd
import mysql.connector
from Config import Config


def db_select(db, sql):
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    return(results)


outfile = "data/snomed_disease_finding_sites.csv"

# Open database connection
config = Config().config
db = mysql.connector.connect(user=config['umls-db']['user'], password=config['umls-db']['password'],
                              host=config['umls-db']['host'],
                              database=config['umls-db']['database'])

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
       "and B.stt = 'PF';")

result = db_select(db, sql)
df = pd.DataFrame(result)

df.to_csv(outfile, index=False)