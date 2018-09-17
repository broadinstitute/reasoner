import copy
import networkx as nx
from neo4j.v1 import GraphDatabase
import neo4j.exceptions
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

    # getters
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

    def get_drug_chebi_ids(self):
        cypher = """
            MATCH (drug:Drug)
            WHERE exists(drug.chebi_id)
            RETURN drug.chebi_id as chebi_id;
            """
        return(self.query(cypher))

    def get_nondrug_chebi_ids(self):
        cypher = """
            MATCH (term:ChebiTerm)
            WHERE not term:Drug
            RETURN term.chebi_id as chebi_id;
            """
        return(self.query(cypher))

    def get_drug_chembl_ids(self):
        cypher = """
            MATCH (d:Drug)
            WHERE exists(d.chembl_id)
            RETURN d.chembl_id as chembl_id
            """
        result = self.query(cypher)
        return([record['chembl_id'] for record in result])

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

    def is_safe(self, x):
        return x is not None and x != ''

    # entity adders
    def add_drug(self, chembl_id, name, cui=None, chebi_id=None, drugbank_id=None, drug_type=None, mechanism=None, pharmacodynamics=None):
        cypher = """MERGE (n:Drug {chembl_id: {chembl_id}})
                    SET n.name = {name}
                 """
        if self.is_safe(cui):
            cypher = cypher + " SET n.cui = {cui} SET n:UmlsTerm "
        if self.is_safe(chebi_id):
            cypher = cypher + " SET n.chebi_id = {chebi_id}"
        if self.is_safe(drugbank_id):
            cypher = cypher + " SET n.drugbank_id = {drugbank_id}"
        if self.is_safe(drug_type):
            cypher = cypher + " SET n.drug_type = {drug_type}"
        if self.is_safe(mechanism):
            cypher = cypher + " SET n.mechanism = {mechanism}"
        if self.is_safe(pharmacodynamics):
            cypher = cypher + " SET n.pharmacodynamics = {pharmacodynamics}"
        try:
            self.query(cypher, chembl_id=chembl_id, name=name, cui=cui, chebi_id=chebi_id,
                   drugbank_id=drugbank_id, drug_type=drug_type, mechanism=mechanism, pharmacodynamics=pharmacodynamics)
        except neo4j.exceptions.ConstraintError:
            print(chembl_id, name, cui, chebi_id, drugbank_id)

    def add_protein(self, uniprot_id, name):
        cypher = """
            MERGE (n:Protein {uniprot_id: {uniprot_id}})
            SET n.name = {name}
            """
        self.query(cypher, uniprot_id=uniprot_id, name=name)

    def add_gene(self, hgnc_id, hgnc_symbol, entrez_id, name):
        cypher = """
            MERGE (n:Gene {hgnc_id: {hgnc_id}})
            SET n.hgnc_symbol = {hgnc_symbol}
            SET n.entrez_id = {entrez_id}
            SET n.name = {name}
            """
        self.query(cypher, hgnc_id=hgnc_id, hgnc_symbol=hgnc_symbol, entrez_id=entrez_id, name=name)

    def add_disease(self, cui, name, mesh_id=None, hpo_id=None):
        cypher = """
            MERGE (n:Disease {cui: {cui}})
            SET n.name =  {name}
            SET n:UmlsTerm
            """
        if self.is_safe(mesh_id):
            cypher = cypher + " SET n.mesh_id = {mesh_id}"
        if self.is_safe(hpo_id):
            cypher = cypher + " SET n.hpo_id = {hpo_id} SET n:HpoTerm;"
        try:
            self.query(cypher, cui=cui, name=name, mesh_id=mesh_id, hpo_id=hpo_id)
        except neo4j.exceptions.ConstraintError:
            print(cui, name, mesh_id, hpo_id)

    def add_pathway(self, go_id, name, cui=None, aspect=None):
        cypher = """
            MERGE (n:Pathway {go_id: {go_id}})
            SET n.name = {name}
            SET n:GoTerm
            """
        if self.is_safe(cui):
            cypher = cypher + " SET n.cui = {cui} SET n:UmlsTerm "
        if self.is_safe(aspect):
            cypher = cypher + " SET n.aspect = {aspect}"
        self.query(cypher, go_id=go_id, cui=cui, aspect=aspect)

    def add_multiclass_term_by_cui(self, cui, name, term_type, id_type=None, alt_id=None):
        cypher = """
            MERGE (n:UmlsTerm {cui: {cui}})
            SET n:%s
            ON CREATE SET n.name = {name}
            """ % term_type
        if self.is_safe(id_type) and self.is_safe(alt_id):
            cypher = cypher + " SET n.%s = {alt_id}" % id_type
        self.query(cypher, name=name, cui=cui, alt_id=alt_id)

    def add_generic_term(self, term_type, id_type, id, name):
        cypher = """
            MERGE (n:%s {%s: {id}})
            SET n.name = {name}
            """ % (term_type, id_type)
        self.query(cypher, id=id, name=name)

    def add_cl_term(self, cl_id, name, cui=None):
        if cui is not None:
            self.add_multiclass_term_by_cui(cui, name, 'ClTerm', 'cl_id', cl_id)
        else:
            self.add_generic_term('ClTerm', 'cl_id', cl_id, name)

    def add_symp_term(self, symp_id, name, cui=None):
        if cui is not None:
            self.add_multiclass_term_by_cui(cui, name, 'SympTerm', 'symp_id', symp_id)
        else:
            self.add_generic_term('SympTerm', 'symp_id', symp_id, name)

    def add_hpo_term(self, hpo_id, name, cui=None):
        if cui is not None:
            self.add_multiclass_term_by_cui(cui, name, 'HpoTerm', 'hpo_id', hpo_id)
        else:
            self.add_generic_term('HpoTerm', 'hpo_id', hpo_id, name)

    def add_uberon_term(self, uberon_id, name, cui=None):
        if cui is not None:
            self.add_multiclass_term_by_cui(cui, name, 'UberonTerm', 'uberon_id', uberon_id)
        else:
            self.add_generic_term('UberonTerm', 'uberon_id', uberon_id, name)

    def add_umls_term(self, cui, name, semtypes=[]):
        cypher = """
            MERGE (n:UmlsTerm {cui: {cui}})
            SET n.name = {name}
            """
        for semtype in semtypes:
            cypher = cypher + "SET n:" + semtype
        self.query(cypher, cui=cui, name=name)



# LOAD CSV WITH HEADERS FROM 'file:///umls2cellontology.csv' AS line
# MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
# SET term.cl_id = line.cl_id
# SET term:ClTerm;

# LOAD CSV WITH HEADERS FROM 'file:///umls2uberon.csv' AS line
# MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
# SET term.uberon_id = line.uberon_id
# SET term:UberonTerm;

# LOAD CSV WITH HEADERS FROM 'file:///umls2symptomontology.csv' AS line
# MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
# SET term.symp_id = line.symp_id
# SET term:SympTerm;

    # relation adders
    def add_drug_target_relation(self,
                   drug_chembl_id,
                   target_type,
                   target_id_type,
                   target_id,
                   activity_value=None,
                   activity_type=None,
                   activity_unit=None):
        cypher = ("MATCH (drug:Drug {chembl_id: {drug_chembl_id}}) " +
                  "MATCH (target:%s {%s: {target_id}}) " % (target_type, target_id_type) +
                  """SET target:Target
                  MERGE (drug)-[r:TARGETS]->(target)
                  SET r.activity_value = {activity_value}
                  SET r.activity_type = {activity_type}
                  SET r.activity_unit = {activity_unit}
                  """)
        self.query(cypher, drug_chembl_id=drug_chembl_id,
                   activity_value=activity_value, activity_type=activity_type, activity_unit=activity_unit, target_id=target_id)

    def add_protein_pathway_relation(self, uniprot_id, go_id, evidence_code=None):
        cypher = """
            MATCH (start:Protein {uniprot_id: {uniprot_id}})
            MATCH (end:Pathway {go_id: {go_id}})
            MERGE (start)-[r:PART_OF]->(end)
            """
        if evidence_code is not None:
            cypher = cypher + " SET r.evidence_code = {evidence_code}"
        self.query(cypher, uniprot_id=uniprot_id, go_id=go_id, evidence_code=evidence_code)

    def add_semmed_relation(self, predicate, start_cui, end_cui, count):
        cypher = """
            MATCH (start:UmlsTerm {cui: {start_cui}})
            MATCH (end:UmlsTerm {cui: {end_cui}})
            MERGE (start)-[r:%s {source: 'semmeddb'}]->(end)
            SET r.count = {count};
            """ % predicate
        self.query(cypher, start_cui=start_cui, end_cui=end_cui, count=count)

    def add_gene_product_relation(self, hgnc_id, uniprot_id):
        self.add_generic_relation("PRODUCT_OF", uniprot_id, "Protein", "uniprot_id", hgnc_id, "Gene", "hgnc_id", "hgnc")

    def add_indication_relation(self, chembl_id, disease_cui):
        self.add_generic_relation("HAS_INDICATION", chembl_id, "Drug", "chembl_id", disease_cui, "Disease", "cui", "chembl")

    def add_disease_finding_site_relation(self, disease_cui, disease_semtype, location_cui, location_semtype):
        self.add_generic_relation("LOCATION_OF", disease_cui, disease_semtype, "cui", location_cui, location_semtype, "cui", "chembl")

    def add_chebi_role_relation(self, start_chebi_id, end_chebi_id, target_name):
        self.add_generic_relation("HAS_ROLE", start_chebi_id, "ChebiTerm", "chebi_id", end_chebi_id, "ChebiTerm", "chebi_id", "chebi")

    def add_isa_relation(self, start_id, start_type, start_id_type, end_id, end_type, end_id_type, source):
        self.add_generic_relation("ISA", start_id, start_type, start_id_type, end_id, end_type, end_id_type, source)

    def add_pert_of_relation(self, start_id, start_type, start_id_type, end_id, end_type, end_id_type, source):
        self.add_generic_relation("PART_OF", start_id, start_type, start_id_type, end_id, end_type, end_id_type, source)

    def add_generic_relation(self, predicate, start_id, start_type, start_id_type, end_id, end_type, end_id_type, source):
        cypher = """
            MATCH (start:%s {%s: {start_id}})
            MATCH (end:%s {%s: {end_id}})
            MERGE (start)-[:%s {source: {source}}]->(end);
            """ % (start_type, start_id_type, end_type, end_id_type, predicate)
        self.query(cypher, start_id=start_id, end_id=end_id, source=source)
