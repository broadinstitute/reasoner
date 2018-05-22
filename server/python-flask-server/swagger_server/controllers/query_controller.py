import datetime

import connexion
import six

from swagger_server.models.query import Query  # noqa: E501
from swagger_server.models.response import Response  # noqa: E501
from swagger_server.models.node import Node
from swagger_server.models.edge import Edge
from swagger_server.models.result_graph import ResultGraph
from swagger_server.models.result import Result
from swagger_server.models.source import Source
from swagger_server import util
from reasoner.KGAgent import KGAgent


def query(body):  # noqa: E501
    """Submit a query to the Indigo question answerer

     # noqa: E501

    :param body: Query information to be submitted
    :type body: dict | bytes

    :rtype: Response
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501

        agent = KGAgent()
        
        if body.query_type == 'cop':
            agent.cop_query(body.terms['drug'], body.terms['disease'])
        elif body.query_type == 'mvp-pathway':
            agent.mvp_target_query(body.terms['drug'])

        graph = agent.get_graph()

        nodes = []
        for node in graph.nodes(data=True):
            node_attributes = {key: value for key, value in node[1].items() if key not in ['labels', 'name']}
            nodes.append(Node(id = node[0], category = ', '.join(node[1]['labels']), name = node[1]['name'], node_attributes = node_attributes))

        edges = []
        for edge in graph.edges(data=True):
            edge_attributes = {key: value for key, value in edge[2].items() if key not in ['type', 'source']}
            if 'source' not in edge[2]:
                edge[2]['source'] = "NA"
            edges.append(Edge(type = edge[2]['type'], source_id = edge[0], target_id = edge[1], origin_list = [Source(name = edge[2]['source'], attribute_list = edge_attributes)]))

        rg = ResultGraph(node_list = nodes, edge_list = edges)
        r = Response(context = "translator_indigo_qa",
                     datetime = str(datetime.datetime.now()),
                     query = body,
                     result_list = [Result(result_graph = rg)])
    return(r)
