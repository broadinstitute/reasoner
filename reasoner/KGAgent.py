from .knowledge_graph.KnowledgeGraph import KnowledgeGraph

class KGAgent:
    def __init__(self):
        self.kg = KnowledgeGraph()
        self.result = None

    def get_result(self):
        return(self.result)

    def get_graph(self):
        if self.result.peek() is not None:
            return(self.kg.get_graph(self.result))
        else:
            return(None)

    def cop_query(self, drug_cui, disease_cui):
        print('\n', drug_cui, disease_cui)
        drug = self.get_drug(drug_cui)
        disease = self.get_disease(disease_cui)

        if drug.peek() is None:
            print('Drug not found.')

        if disease.peek() is None:
            print('Disease not found.')

        self.result = self.cop_drug_category(drug_cui, disease_cui)

        #     for record in result:
        #         print(record['cat'].properties['name'])
        #         res = self.target_by_drug_category(drug_cui, record['cat'].properties['cui'])
        #         for rec in res:
        #             print(rec)
        # else:
        #     result = self.cop_targets(drug_cui, disease_cui)
        #     for record in result:
        #         print(record)

        # result = self.cop_full(drug_cui, disease_cui)
        # print(len(list(result.records())))


    def mvp_target_query(self, drug_chembl_id):
        self.result = self.drug2target(drug_chembl_id)



    # def cop_drug_category(self, drug_cui, disease_cui):
    #     result = self.kg.query("""
    #              MATCH path = (dr:Drug {cui:{drug_cui}})-[:HAS_ROLE]->(cat:ChebiTerm)-[:TREATS]->(di:Disease {cui:{disease_cui}})
    #              RETURN cat
    #              """,
    #              drug_cui=drug_cui, disease_cui=disease_cui)
    #     return(result)

    def cop_drug_category(self, drug_cui, disease_cui):
        result = self.kg.query("""
                 MATCH path = (dr:Drug {cui:{drug_cui}})-[:HAS_ROLE]->(cat:ChebiTerm)-[:TREATS]->(di:Disease {cui:{disease_cui}})
                 UNWIND nodes(path) as n
                 UNWIND relationships(path) as r
                 RETURN collect(distinct n) as nodes, collect(distinct r) as edges
                 """,
                 drug_cui=drug_cui, disease_cui=disease_cui)
        return(result)

    def target_by_drug_category(self, drug_cui, category_cui):
        result = self.kg.query("""
                     MATCH (ta:Target)<-[:TARGETS]-(dr:Drug {cui:{drug_cui}})-[:HAS_ROLE]->(cat:ChebiTerm {cui: {category_cui}})<-[:HAS_ROLE]-(:Drug)-[:TARGETS]->(ta)
                     RETURN ta, count(*)
                     """, drug_cui=drug_cui, category_cui=category_cui)
        return(result)

    def cop_targets(self, drug_cui, disease_cui):
        result = self.kg.query("""
                 MATCH path = (dr:Drug {cui:{drug_cui}})-[:TARGETS]->(ta:Target)<-[:TARGETS]-(:ChebiTerm)-[:HAS_ROLE]->(cat:ChebiTerm)-[:TREATS]->(di:Disease {cui:{disease_cui}})
                 RETURN cat, count(*)
                 """,
                 drug_cui=drug_cui, disease_cui=disease_cui)
        return(result)

    def get_drug(self, cui):
        result = self.kg.query("MATCH (n:Drug {cui:{cui}})RETURN n",
                 cui=cui)
        return(result)

    def get_disease(self, cui):
        result = self.kg.query("MATCH (n:Disease {cui:{cui}})RETURN n",
                 cui=cui)
        return(result)

    def cop_full(self, drug_cui, disease_cui):
        result = self.kg.query("""
                 MATCH path = (dr:Drug {cui:{drug_cui}})--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(sy:Symptom)--(di:Disease {cui:{disease_cui}})
                 RETURN path
                 """,
                 drug_cui=drug_cui, disease_cui=disease_cui)
        return(result)

    def drug2target(self, drug_chembl_id):
        result = self.kg.query("""
                 MATCH path = (dr:Drug {chembl_id:{drug_chembl_id}})--(ta:Target)
                 UNWIND nodes(path) as n
                 UNWIND relationships(path) as r
                 RETURN collect(distinct n) as nodes, collect(distinct r) as edges
                 """,
                 drug_chembl_id=drug_chembl_id)
        return(result)

    def pathwayToGenes(self, pathway_go_id):
        self.result = self.kg.query("""
         MATCH path = (pa:Pathway {go_id:{pathway_go_id}})<-[:PART_OF]-(ta:Target)
         UNWIND nodes(path) as n
         UNWIND relationships(path) as r
         RETURN collect(distinct n) as nodes, collect(distinct r) as edges
         """,
         pathway_go_id=pathway_go_id)

    def geneToCompound(self, gene_hgnc_id):
        self.result = self.kg.query("""
         MATCH path = (ta:Target {hgnc_id:{gene_hgnc_id}})<-[:TARGETS]-(dr:Drug)
         UNWIND nodes(path) as n
         UNWIND relationships(path) as r
         RETURN collect(distinct n) as nodes, collect(distinct r) as edges
         """,
         gene_hgnc_id=gene_hgnc_id)

    def compoundToIndication(self, drug_chembl_id):
        self.result = self.kg.query("""
         MATCH path = (dr:Drug {chembl_id:{drug_chembl_id}})-[:HAS_INDICATION]->(di:Disease)
         UNWIND nodes(path) as n
         UNWIND relationships(path) as r
         RETURN collect(distinct n) as nodes, collect(distinct r) as edges
         """,
         drug_chembl_id=drug_chembl_id)

    def compoundToPharmClass(self, drug_chembl_id):
        self.result = self.kg.query("""
         MATCH path = (dr:Drug {chembl_id:{drug_chembl_id}})-[:HAS_ROLE]->(ct:ChebiTerm)
         UNWIND nodes(path) as n
         UNWIND relationships(path) as r
         RETURN collect(distinct n) as nodes, collect(distinct r) as edges
         """,
         drug_chembl_id=drug_chembl_id)

    def symptomToDisease(self, symptom_umls_id):
        cypher = """
            MATCH path = (sy:Symptom {cui:{umls_id}})-[:ASSOCIATED_WITH]->(di:Disease)
            UNWIND nodes(path) as n
            UNWIND relationships(path) as r
            RETURN collect(distinct n) as nodes, collect(distinct r) as edges"""
        self.result = self.kg.query(cypher, umls_id=symptom_umls_id)
