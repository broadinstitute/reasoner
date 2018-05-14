import copy
import networkx as nx
from neo4j.v1 import GraphDatabase
from .Config import Config


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

    def get_drugs(self):
        cypher = """
            MATCH (drug:Drug)
            WHERE exists(drug.chebi_id)
            RETURN drug.chebi_id as chebi_id;
            """
        return(self.query(cypher))

    def get_chebi_terms(self):
        cypher = """
            MATCH (term:ChebiTerm)
            WHERE not term:Drug
            RETURN term.chebi_id as chebi_id;
            """
        return(self.query(cypher))

    def get_chembl_ids(session):
        cypher = """
            MATCH (d:Drug)
            WHERE exists(d.chembl_id)
            RETURN d.chembl_id as chembl_id
            """
        result = self.query(cypher)
        return([record['chembl_id'] for record in result])

    def add_chebi_role(self, origin_chebi_id, target_chebi_id, target_name):
        cypher = """
            MATCH (origin:ChebiTerm {chebi_id: {origin_chebi_id}})
            MERGE (target:ChebiTerm {chebi_id: {target_chebi_id}})
            SET target.name = {target_name}
            MERGE (origin)-[:HAS_ROLE {source: 'chebi'}]->(target);
            """
        self.query(cypher, origin_chebi_id=origin_chebi_id, target_chebi_id=target_chebi_id, target_name=target_name)

    def add_indication(self, chembl_id, disease_cui, disease_name):
        cypher = """
            MATCH (drug:Drug {chembl_id: {chembl_id}})
            MATCH (disease:Disease {cui: {disease_cui}})
            SET disease.name = {disease_name}
            MERGE (drug)-[:HAS_INDICATION]->(disease)
            """
        self.query(cypher, chembl_id=chembl_id, disease_cui=disease_cui, disease_name=disease_name)

    def set_semtype(self, cui, semtype):
        cypher = """
            MATCH (term {cui: {cui}})
            SET term:%s
            """ % (semtype)
        self.query(cypher, cui=cui)

    def get_cuis(self):
        cypher = """
            MATCH (n)
            WHERE exists(n.cui)
            RETURN n.cui as cui
            """
        result = self.query(cypher)
        return([record['cui'] for record in result])

    def add_drug(self, cui, chembl_id=None, chebi_id=None, drugbank_id=None):
        cypher = "MERGE (n {cui: {cui}}) SET n :Drug"
        if chembl_id is not None:
            cypher = cypher + " SET chembl_id = {chembl_id}"
        if chebi_id is not None:
            cypher = cypher + " SET chebi_id = {chebi_id}"
        if drugbank_id is not None:
            cypher = cypher + " SET drugbank_id = {drugbank_id}"
        self.query(cypher, chembl_id=chembl_id, chebi_id=chebi_id, drugbank_id=drugbank_id)

    def add_chembl_target(self, drug_chembl_id, target_uniprot_id, target_name,
                          activity_value=None,
                          activity_type=None,
                          activity_unit=None):
        cypher = """
            MATCH (drug:Drug {chembl_id: {drug_chembl_id}})
            MERGE (target:Target {uniprot_id: {target_uniprot_id}})
            MERGE (drug)-[r:TARGETS]->(target)
            SET target.name = {target_name};
            SET r.activity_value = {activity_value}
            SET r.activity_type = {activity_type}
            SET r.activity_unit = {activity_unit}
            """
        self.query(cypher, drug_chembl_id=drug_chembl_id, target_uniprot_id=target_uniprot_id, target_name=target_name,
                   activity_value=activity_value, activity_type=activity_type, activity_unit=activity_unit)
