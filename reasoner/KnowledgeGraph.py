import copy
import networkx as nx
from neo4j.v1 import GraphDatabase
from .neo4j.Config import Config


class KnowledgeGraph:
    def __init__(self):
        config = Config().config
        self.driver = GraphDatabase.driver(config['neo4j']['host'],
                                           auth=(config['neo4j']['user'],
                                                 config['neo4j']['password']))

    def query(self, query, **kwargs):
        with self.driver.session() as session:
            result = session.run(query, **kwargs)
        return(result)

    def get_graph(self, results):
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
