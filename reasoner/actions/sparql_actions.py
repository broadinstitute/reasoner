from SPARQLWrapper import SPARQLWrapper, JSON
from .action import Action

class WikiPWTargetToPathway(Action):

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
      if pname not in pathway_names:
        pathways.append({'Pathway':[{'node':{'name':pname}, 'edge':{}}]})
        pathway_names.append(pname)

    return(pathways)