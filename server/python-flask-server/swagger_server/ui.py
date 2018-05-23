import datetime

from reasoner.KGAgent import KGAgent
from swagger_server.models.response import Response  # noqa: E501
from swagger_server.models.node import Node
from swagger_server.models.edge import Edge
from swagger_server.models.node import NodeAttribute
from swagger_server.models.edge import EdgeAttribute
from swagger_server.models.result_graph import ResultGraph
from swagger_server.models.result import Result


def resultGraph(graph):
    nodes = []
    for node in graph.nodes(data=True):
        node_attributes = [NodeAttribute(name=key,
                                         value=value)
                           for key, value in node[1].items()
                           if key not in ['labels', 'name']]
        nodes.append(Node(id=node[0],
                          type=', '.join(node[1]['labels']),
                          name=node[1]['name'],
                          node_attributes=node_attributes))

    edges = []
    for edge in graph.edges(data=True):
        edge_attributes = [EdgeAttribute(name=key,
                                         value=value)
                           for key, value in edge[2].items()
                           if key not in ['type', 'source']]
        if 'source' not in edge[2]:
            edge[2]['source'] = "NA"
        edges.append(Edge(type=edge[2]['type'],
                          source_id=edge[0],
                          target_id=edge[1],
                          provided_by=edge[2]['source'],
                          attribute_list=edge_attributes))

    rg = ResultGraph(node_list=nodes, edge_list=edges)
    return(rg)


def cop_query(drug, disease):
    agent = KGAgent()
    agent.cop_query(drug, disease)
    graph = agent.get_graph()
    rg = resultGraph(graph)
    r = Response(context="translator_indigo_qa",
                 datetime=str(datetime.datetime.now()),
                 result_list=[Result(result_graph=rg)])
    return(r)


def mvp_target_query(chemical_substance):
    agent = KGAgent()
    agent.mvp_target_query(chemical_substance)
    graph = agent.get_graph()
    start_node = filter(lambda n, d: d['chembl_id'] == chemical_substance,
                        graph.nodes(data=True))
    neighbors = graph[start_node]
    print(neighbors)

    rg = resultGraph(graph)
    r = Response(context="translator_indigo_qa",
                 datetime=str(datetime.datetime.now()),
                 result_list=[Result(result_graph=rg)])
    return(r)

