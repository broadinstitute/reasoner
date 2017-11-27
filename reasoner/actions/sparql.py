"""A set of SPAQRL-based actions.
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from .action import Action

class WikiPWTargetToPathway(Action):
    """Use WikiPathways to find pathways given a target.
    """
    def __init__(self):
        super().__init__(['bound(Target)'],['bound(Pathway) and connected(Target, Pathway)'])
        self.sparql = SPARQLWrapper("http://sparql.wikipathways.org/")

    def send_query(self, gene_symbol):
        query = """
        PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX cur: <http://vocabularies.wikipathways.org/wp#Curation:>

        SELECT DISTINCT ?pathway str(?title) as ?pathwayTitle
        WHERE {
          ?geneProduct a wp:GeneProduct .
          ?geneProduct rdfs:label ?label .
          ?geneProduct dcterms:isPartOf ?pathway .
          ?pathway wp:ontologyTag ?tag.
          ?pathway a wp:Pathway ;
            dc:title ?title.

          FILTER (str(?label)= "%s" && (?tag=cur:Reactome_Approved || ?tag=cur:AnalysisCollection)).
        }
        """ % gene_symbol

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())

    def execute(self, query):
        results = self.send_query(query['Target'])

        pathways = list()
        pathway_names = list()
        for result in results["results"]["bindings"]:
            pname = result["pathwayTitle"]["value"].lower()
            uri = result["pathway"]["value"]
            if pname not in pathway_names:
                pathways.append({'Pathway':[{'node':{'name':pname, 'uri':uri}, 'edge':{}}]})
                pathway_names.append(pname)

        return(pathways)



class WikiPWPathwayToCell(Action):
    """Use WikiPathways to find cells given a pathway.
    """
    def __init__(self):
        super().__init__(['bound(Pathway)'],['bound(Cell) and connected(Pathway, Cell)'])
        self.sparql = SPARQLWrapper("http://sparql.wikipathways.org/")

    def send_query(self, pathway_id):
        query = """
            PREFIX wp:      <http://vocabularies.wikipathways.org/wp#> 
            PREFIX dc:      <http://purl.org/dc/elements/1.1/> 
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#> 

            SELECT DISTINCT ?coTerm ?label
            WHERE {
                ?pathwayRDF wp:ontologyTag ?coTerm .
                ?pathwayRDF dcterms:identifier "%s"^^xsd:string
                FILTER regex(str(?coTerm), "^http://purl.obolibrary.org/obo/CL_").

                SERVICE <http://sparql.hegroup.org/sparql/>
                {
                    ?coTerm rdfs:label ?label .
                }
            }
            """ % pathway_id

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())

    def execute(self, query):
        results = self.send_query(query['Pathway'])

        cells = list()
        for result in results["results"]["bindings"]:
            cells.append({'Cell':[{'node':{'name':result["label"]["value"], 'uri':result["coTerm"]["value"]}, 'edge':{}}]})

        return(cells)



class DiseaseOntologyConditionToGeneticCondition(Action):
    """Use the Disease Ontology to identify whether a condition has a genetic cause.
    """
    def __init__(self):
        super().__init__(['bound(Condition)'],['connected(Condition, GeneticCondition)'])
        self.sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql/")

    def send_query(self, query):
        query = """
                PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX obo-term: <http://purl.obolibrary.org/obo/>
                SELECT DISTINCT ?y as ?doid ?x ?label as ?genetic_condition
                from <http://purl.obolibrary.org/obo/merged/DOID>
                WHERE
                {
                VALUES ?x { obo-term:DOID_630 obo-term:DOID_655 obo-term:DOID_2214 }
                ?y rdfs:subClassOf* ?x.
                ?x rdfs:label ?label.
                ?y rdfs:label|oboInOwl:hasExactSynonym|oboInOwl:hasNarrowSynonym ?query.
                FILTER(lcase(str(?query))="%s")
                }
                """ % query.lower()

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())

    def execute(self, query):
        results = self.send_query(query['Condition'])

        genetic_conditions = list()
        for result in results["results"]["bindings"]:
            name = result["genetic_condition"]["value"]
            doid = result["doid"]["value"]
            genetic_conditions.append({'GeneticCondition':[{'node':{'name':name, 'id':doid}, 'edge':{}}]})

        return(genetic_conditions)