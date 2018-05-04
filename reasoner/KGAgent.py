from .KnowledgeGraph import KnowledgeGraph

class KGAgent:
    def __init__(self):
        self.kg = KnowledgeGraph()

    def cop_query(self, drug_cui, disease_cui):
        print('\n', drug_cui, disease_cui)
        drug = self.get_drug(drug_cui)
        disease = self.get_disease(disease_cui)

        if drug.peek() is None:
            print('Drug not found.')

        if disease.peek() is None:
            print('Disease not found.')

        result = self.cop_drug_category(drug_cui, disease_cui)
        if result.peek() is not None:
            for record in result:
                print(record['cat'].properties['name'])
                res = self.target_by_drug_category(drug_cui, record['cat'].properties['cui'])
                for rec in res:
                    print(rec)
        else:
            result = self.cop_targets(drug_cui, disease_cui)
            for record in result:
                print(record)

        result = self.cop_full(drug_cui, disease_cui)
        print(len(list(result.records())))



    def cop_drug_category(self, drug_cui, disease_cui):
        result = self.kg.query("""
                 MATCH path = (dr:Drug {cui:{drug_cui}})-[:HAS_ROLE]->(cat:ChebiTerm)-[:TREATS]->(di:Disease {cui:{disease_cui}})
                 RETURN cat
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
                 MATCH path = (dr:Drug {cui:{drug_cui}})--(ta:Target)--(p:Pathway)-[*1..3]-(di:Disease {cui:{disease_cui}})
                 RETURN path
                 """,
                 drug_cui=drug_cui, disease_cui=disease_cui)
        return(result)
