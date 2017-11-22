from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.request, urllib.parse
import json

class MeSH:
    
    def __init__(self):
        super().__init__()
        self.sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
        self.url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        
    def sparql_synonym_query(self, query):
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        
        SELECT DISTINCT ?x ?pref_label ?alt_label
        FROM <http://id.nlm.nih.gov/mesh>
        WHERE {
          ?x meshv:altLabel ?alt_label.
          ?x meshv:prefLabel ?pref_label.
          FILTER(str(?alt_label)="%s")
        }  
        """ % query
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())
    
    def parse_request(self, url):
        with urllib.request.urlopen(url) as response:
            res = response.read().decode()
        return json.loads(res)
    
    def esearch(self, term):
        query = 'esearch.fcgi?db=mesh&term=' + urllib.parse.quote_plus(term) + '&retmode=json'
        res = self.parse_request(self.url_prefix + query)
        return(res)