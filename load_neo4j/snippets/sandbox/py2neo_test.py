import re
import pandas as pd
from py2neo import Graph
import networkx as nx
from reasoner.knowledge_graph.Config import Config

config = Config().config
print(config['neo4j']['host'])
graph = Graph(host='indigo.ncats.io', auth=(config['neo4j']['user'], config['neo4j']['password']))

query = """
MATCH (d:Drug)-->(ta:Target)
WHERE d.name = 'Captopril'
RETURN d, ta
"""

data = graph.run(query)

for d in data:
    print(d)


g = data.get_graph()
nx.draw(g)
