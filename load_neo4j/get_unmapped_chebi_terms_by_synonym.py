import csv
import pandas
from SPARQLWrapper import SPARQLWrapper, JSON
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

def sparql_query(sparql, chebi_id):
    sparql.setQuery("""
            PREFIX obo-term: <http://purl.obolibrary.org/obo/>
            SELECT DISTINCT ?x ?label
            FROM <http://purl.obolibrary.org/obo/merged/CHEBI>
            WHERE {
            obo-term:%s <http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym> ?label.
            }
        """ % chebi_id.replace(":", "_"))
    return(sparql.query().convert())


infile  = '../data/neo4j/chebi2umls_by_name.csv'
chebi2umls = pandas.read_csv(infile)

unmapped = chebi2umls.loc[chebi2umls['cui'] == 'NONE']

sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql/")
sparql.setReturnFormat(JSON)

outfile = '../data/neo4j/chebi2umls_by_synonym.csv'

mappings = [['chebi_id', 'chebi_name', 'synonym', 'cui', 'umls_name']]
uq = UmlsQuery()
for index, row in unmapped.iterrows():
    print(row['chebi_id'])
    results = sparql_query(sparql, row['chebi_id'])
    for result in results['results']['bindings']:
        umls_result = uq.search(result['label']['value'])
        if umls_result:
            mappings.append([row['chebi_id'], row['chebi_name'], result['label']['value'], umls_result['results'][0]['ui'], umls_result['results'][0]['name']])


with open(outfile, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(mappings)