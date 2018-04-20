import copy
import re
import pandas as pd
import networkx as nx
from neo4j.v1 import GraphDatabase
from Config import Config



def get_graph(results):
    graph = nx.MultiDiGraph()
    
    for record in results:
        for node in record['nodes']:
            properties = copy.deepcopy(node.properties)
            properties['labels'] = node.labels
            graph.add_node(node.id, **properties)
        for edge in record['edges']:
            properties = copy.deepcopy(edge.properties)
            properties.update(
                id=edge.id,
                type=edge.type
            )
            graph.add_edge(edge.start, edge.end,
                           key=edge.type, **properties)
    return graph


def get_cop(session, drug, disease):
    result = session.run("""MATCH path = (dr:Drug {name: '%s'})-[*..6]-(di:Disease {name:'%s'})
                         UNWIND nodes(path) as n
                         UNWIND relationships(path) as r
                         RETURN collect(distinct n) as nodes, collect(distinct r) as edges""" % (drug, disease.replace("'", "")))

    return(result)


# Open database connection
config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'],
                              auth=(config['neo4j']['user'],
                                    config['neo4j']['password']))

cop_file = './data/cop_benchmark.csv'
cop = pd.read_csv(cop_file)

with driver.session() as session:
    for index, row in cop.iterrows():
        result = get_cop(session,
                         row['Drug'].lower().capitalize(),
                         row['ConditionName'].lower().capitalize())
        for record in result:
            print(row['Drug'], row['ConditionName'], record)


    # result = get_cop(session,
    #                  'Naproxen',
    #                  'Osteoarthritis')
    
    # G = get_graph(result)
    # print(list(G.nodes(data=True)))

    # print(list(G.edges(data=True)))



