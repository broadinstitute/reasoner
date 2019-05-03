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
from openapi_server.models.message_terms import MessageTerms


def resultGraph(graph):
    nodes = []
    for node in graph.nodes(data=True):
        node_attributes = [NodeAttribute(name=key,
                                         value=str(value))
                           for key, value in node[1].items()
                           if key not in ['labels', 'name']]
        nodes.append(Node(id=str(node[0]),
                          type=[str(label) for label in node[1]['labels']],
                          name=str(node[1]['name']),
                          node_attributes=node_attributes))

    edges = []
    for edge in graph.edges(data=True):
        edge_attributes = [EdgeAttribute(name=key,
                                         value=str(value))
                           for key, value in edge[2].items()
                           if key not in ['type', 'source','id']]
        if 'source' not in edge[2]:
            edge[2]['source'] = "NA"
        edges.append(Edge(type=edge[2]['type'],
                          source_id=str(edge[0]),
                          target_id=str(edge[1]),
                          provided_by=str(edge[2]['source']),
                          id=str(edge[2]['id']),
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

def queryReasoner(query_type_id, terms):

    r = 'wrong query_message.query_type_id \''+str(query_type_id)+'\''
    if query_type_id == 'Q2':
        r = cop_query(terms.chemical_substance, terms.disease)
    elif query_type_id == 'Q3':
        r = mvp_target_query(terms.chemical_substance)
    elif query_type_id == 'conditionToSymptoms':
        r = conditionToSymptoms(terms.disease)
    elif query_type_id == 'symptomToConditions':
        r = symptomToConditions(terms.symptom)
    elif query_type_id == 'conditionSymptomSimilarity':
        r = conditionSymptomSimilarity(terms.disease)
    elif query_type_id == 'genesToPathways':
        r = genesToPathways(terms.gene)
    elif query_type_id == 'pathwayToGenes':
        r = pathwayToGenes(terms.pathway)
    elif query_type_id == 'geneToCompound':
        r = geneToCompound(terms.gene)
    elif query_type_id == 'compoundToIndication':
        r = compoundToIndication(terms.chemical_substance)
    elif query_type_id == 'compoundToPharmClass':
        r = compoundToPharmClass(terms.chemical_substance)
    else:
        msg =  "query_message.query_type_id '"+str(query_type_id)+"' not implemented"
        return( { "status": 501, "title": msg, "detail": msg, "type": "about:blank" }, 501 )

    return r

def knowledgeMap():
    """
        Knowledge-map format: list of:
            ( subject=("biolink_type","?/*", "indigo_reasoner_type"),
              predicate,
              object =("biolink_type","?/*", "indigo_reasoner_type"),
              "query_type_id"
            )
            "?" - map node to query_message.terms
            "*" - wildcard
    """
    km = [
        (("chemical_substance","?","chemical_substance"),"associated_with",("disease","?","disease"), "Q2"),
        (("chemical_substance","?","chemical_substance"),"targets",("protein","*"), "Q3"),
        (("phenotypic_feature","*"),"associated_with",("disease","?","disease"), "conditionToSymptoms"),
        (("phenotypic_feature","?","symptom"),"associated_with",("disease","*"), "symptomToConditions"),
        (("chemical_substance","*"),"targets",("gene","?","gene"), "geneToCompound"),
        (("chemical_substance","?","chemical_substance"),"has_indication",("disease","*"), "compoundToIndication"),
        (("chemical_substance","?","chemical_substance"),"has_role",("pharmacological_class","*"), "compoundToPharmClass")
    ]
    return km

def node2tuple(node):
    return (node.type, node.curie)

def queryGraph2triples(query_graph):
    nodes = {}
    for node in query_graph.nodes:
        nodes[node.node_id] = node
    triples = []
    for edge in query_graph.edges:
        source_node = nodes[edge.source_id]
        edge_type = edge.type
        target_node = nodes[edge.target_id]
        triple = (node2tuple(source_node), edge_type, node2tuple(target_node))
        triples.append(triple)
    return triples


def match_triple(query_triples, km_triple):
    terms = MessageTerms()
    if len(query_triples)!= 1:
        return None
    query_triple = query_triples[0]

    if km_triple[0][0] != query_triple[0][0]:
        return None
    if query_triple[1] != None and km_triple[1] != query_triple[1]:
        return None
    if km_triple[2][0] != query_triple[2][0]:
        return None

    if km_triple[0][1] == '?' and  query_triple[0][1] == None:
        return None
    if km_triple[0][1] == '*' and  query_triple[0][1] != None:
        return None
    if km_triple[0][1] == '?' and  query_triple[0][1] != None:
        setattr(terms, '_'+km_triple[0][2], query_triple[0][1])

    if km_triple[2][1] == '?' and  query_triple[2][1] == None:
        return None
    if km_triple[2][1] == '*' and  query_triple[2][1] != None:
        return None
    if km_triple[2][1] == '?' and  query_triple[2][1] != None:
        setattr(terms, '_'+km_triple[2][2], str(query_triple[2][1]))


    return (km_triple[3], terms)

def queryGraph2query(query_graph):
    """
        translate query_graph to query_type_id and query_message.terms
        and query reasoner
    """
    query_triples = queryGraph2triples(query_graph)
    for km_triple in knowledgeMap():
        match = match_triple(query_triples, km_triple)
        if match != None:
            query_type_id, terms = match
            return queryReasoner(query_type_id, terms)
    msg =  "graph query not implemented"
    return( { "status": 501, "title": msg, "detail": msg, "type": "about:blank" }, 501 )

