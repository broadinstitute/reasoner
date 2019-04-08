import datetime

from reasoner.KGAgent import KGAgent
##from openapi_server.models.response import Response  # noqa: E501
from openapi_server.models.message import Message
from openapi_server.models.node import Node
from openapi_server.models.edge import Edge
from openapi_server.models.node_attribute import NodeAttribute
from openapi_server.models.edge_attribute import EdgeAttribute
from openapi_server.models.knowledge_graph import KnowledgeGraph
from openapi_server.models.result import Result


def resultGraph(graph):
    nodes = []
    for node in graph.nodes(data=True):
        node_attributes = [NodeAttribute(name=key,
                                         value=value)
                           for key, value in node[1].items()
                           if key not in ['labels', 'name']]
        nodes.append(Node(id=str(node[0]),
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
                          source_id=str(edge[0]),
                          target_id=str(edge[1]),
                          provided_by=edge[2]['source'],
                          edge_attributes=edge_attributes))

    rg = KnowledgeGraph(nodes=nodes, edges=edges)
    return(rg)

def getDefaultResponse(agent):
    graph = agent.get_graph()
    rg = resultGraph(graph)
    r = Message(context="translator_indigo_qa",
                 datetime=str(datetime.datetime.now()),
                 results=[Result(result_graph=rg)])
    return(r)

def cop_query(drug, disease):
    agent = KGAgent()
    agent.cop_query(drug, disease)
    return(getDefaultResponse(agent))

def mvp_target_query(chemical_substance):
    agent = KGAgent()
    agent.mvp_target_query(chemical_substance)
    graph = agent.get_graph()

    chembl_id = chemical_substance
    start_node = [n for n,d in graph.nodes(data=True) if 'chembl_id' in d and d['chembl_id'] == chembl_id][0]
    neighbors = graph[start_node]

    results = []
    for neighbor in neighbors:
        subgraph = graph.subgraph([start_node, neighbor])
        rg = resultGraph(subgraph)
        results.append(Result(result_graph=rg))

    r = Message(context="translator_indigo_qa",
                 datetime=str(datetime.datetime.now()),
                 results=results)
    return(r)


def conditionToSymptoms(disease):
    agent = KGAgent()
    agent.diseaseToSymptom(disease)
    return(getDefaultResponse(agent))

def symptomToConditions(symptom):
    agent = KGAgent()
    agent.symptomToDisease(symptom)
    return(getDefaultResponse(agent))

def conditionSymptomSimilarity(disease):
    agent = KGAgent()
    agent.conditionSymptomSimilarity(disease)
    return(getDefaultResponse(agent))

def genesToPathways(genes):
    return(None)

def pathwayToGenes(pathway):
    agent = KGAgent()
    agent.pathwayToGenes(pathway)
    return(getDefaultResponse(agent))

def geneToCompound(gene):
    agent = KGAgent()
    agent.geneToCompound(gene)
    return(getDefaultResponse(agent))

def compoundToIndication(chemical_substance):
    agent = KGAgent()
    agent.compoundToIndication(chemical_substance)
    return(getDefaultResponse(agent))

def compoundToPharmClass(chemical_substance):
    agent = KGAgent()
    agent.compoundToPharmClass(chemical_substance)
    return(getDefaultResponse(agent))
