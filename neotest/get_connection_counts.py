from neo4j.v1 import GraphDatabase
from Config import Config


def get_connection_count(session, a, b):
    counts = {}
    result = session.run(
        'match (a:%s)-->(b:%s) return count(*) as n;' % (a, b))
    counts[a + '2' + b] = [record['n'] for record in result][0]
    result = session.run(
        'match (a:%s)<--(b:%s) return count(*) as n;' % (a, b))
    counts[b + '2' + a] = [record['n'] for record in result][0]
    return(counts)


config = Config().config
driver = GraphDatabase.driver(
    config['neo4j']['host'],
    auth=(config['neo4j']['user'], config['neo4j']['password']))

path = ['Drug', 'Target', 'Pathway', 'Cell', 'Tissue', 'Symptom', 'Disease']


with driver.session() as session:
    for i in range(len(path) - 1):
        print(get_connection_count(session, path[i], path[i + 1]))
