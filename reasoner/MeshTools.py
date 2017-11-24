from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.request, urllib.parse
import json
import xmltodict
import xml.etree.ElementTree as etree
import sqlite3

class Eutilities():
    def __init__(self):
        self.url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        
    def get_request(self, url):
        with urllib.request.urlopen(url) as response:
            res = response.read().decode()
        return res

    def get_json_request(self, url):
        return self.parse_json(self.get_request(url))
    
    def get_xml_request(self, url):
        return self.parse_xml(self.get_request(url))
    
    def parse_json(self, obj):
        return json.loads(obj)
    
    def parse_xml(self, obj):
        return xmltodict.parse(obj)
    
    def esearch(self, term, db, retmax = 20, retmode = "json"):
        query = 'esearch.fcgi?db=' + db +'&term=' + urllib.parse.quote_plus(term) + '&retmode=' + retmode +'&retmax=' + str(retmax)
        res = self.get_json_request(self.url_prefix + query)
        return res
    
    def esummary(self, entry_id, db, retmode="json"):
        query = 'esummary.fcgi?db=' + db +'&id=' + entry_id + '&retmode=' + retmode
        res = self.get_json_request(self.url_prefix + query)
        return res
    
    def efetch(self, entry_id, db, rettype = None, retmode = None):
        query = 'efetch.fcgi?db=' + db + '&id=' + entry_id
        if rettype is not None:
            query = query + '&rettype=' + rettype
        if retmode is not None:
            query = query + '&retmode=' + retmode
        
        url = self.url_prefix + query
        with urllib.request.urlopen(url) as response:
            res = response.read()
        return res


class MeshTools(Eutilities):
    
    def __init__(self):
        super().__init__()
        self.sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
        self.source_file = '../reasoner/data/MeSH_hierarchy.txt'
        self.db = './data/reasoner_data.sqlite'
        self.db_conn = sqlite3.connect(self.db)
        
    def sparql_synonym_query(self, query):
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        
        SELECT DISTINCT ?x ?pref_label ?rdfs_label
        FROM <http://id.nlm.nih.gov/mesh>
        WHERE {
          ?x meshv:altLabel|meshv:prefLabel|rdfs:label ?query.
          ?x meshv:prefLabel ?pref_label.
          ?x rdfs:label ?rdfs_label.
          FILTER(lcase(str(?query))="%s")
        }  
        """ % query
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())
    
    def id2treenums(self, mesh_id):
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        
        SELECT DISTINCT ?treenum
        FROM <http://id.nlm.nih.gov/mesh>
        WHERE {
          mesh:%s meshv:treeNumber ?treenum.
        }  
        """ % mesh_id
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        
        result = self.sparql.query().convert()
        
        treenums = list()
        for entry in result['results']['bindings']:
            treenums.append(entry['treenum']['value'][27:])     
        return treenums
    
    def id2entity_sparql(self, mesh_id):
        treenums = self.id2treenums(mesh_id)
        return self.treenums2entity(treenums)
    
    def id2entity(self, mesh_id):
        c = self.db_conn.cursor()
        result = next(iter(c.execute('SELECT entity, bound FROM mesh WHERE mesh_ui = "%s"' % mesh_id).fetchall()), [])
        if len(result) == 0:
            return (None, False)
        return result
    
    def get_terms(self, query):
        search_results = self.esearch(query + '[MeSH Term]', 'mesh')
        if len(search_results['esearchresult']['idlist']) == 0:
            search_results = self.esearch(query, 'mesh')
        
        if len(search_results['esearchresult']['idlist']) == 0:
            return []
        
        uid = ','.join(search_results['esearchresult']['idlist'])
        summary = self.esummary(uid, 'mesh')
        
        terms = list()
        for uid in summary['result']['uids']:
            entry = summary['result'][uid]
            treenums = [x['treenum'] for x in entry['ds_idxlinks']]
            term = entry['ds_meshterms'][0]
            mesh_id = entry['ds_meshui']
            terms.append({'term':term, 'treenums':treenums, 'mesh_id':mesh_id})
        return(terms)
    
    def get_best_term(self, query):
        terms = self.get_terms(query)
        return(next(iter(terms), []))
    
    def get_term_entities(self, query):
        terms = self.get_terms(query)
        if len(terms) == 0:
            return []
        for term in terms:
            (term['entity'], term['bound']) = self.id2entity(term['mesh_id'])
        return(terms)                   
    
    def get_best_term_entity(self, query):
        term = self.get_best_term(query)
        if len(term) ==0:
            return {'entity':None, 'bound':False}
        (term['entity'], term['bound']) = self.id2entity(term['mesh_id'])
        return(term)
    
    def treenums2entity(treenums):
            bound = True

            if any([treenum.startswith('D02') for treenum in treenums]):
                if any([treenum in ['D02'] for treenum in treenums]):
                    bound = False
                return ('Drug', bound)

            elif any([treenum.startswith('D12.776') for treenum in treenums]) or any([treenum.startswith('D08.811') for treenum in treenums]):
                if any([treenum in ['D12.776', 'D08.811'] for treenum in treenums]):
                    bound = False
                return ('Target', bound)

            elif any([treenum.startswith('G03.493') for treenum in treenums]) or any([treenum.startswith('G04.835') for treenum in treenums]):
                if any([treenum in ['G03.493', 'G04.835'] for treenum in treenums]):
                    bound = False
                return ('Pathway', bound)

            elif any([treenum.startswith('A11') for treenum in treenums]):
                if any([treenum in ['A11', 'A11.251', 'A11.251.210'] for treenum in treenums]):
                    bound = False
                return ('Cell', bound)

            elif any([treenum.startswith('C23') for treenum in treenums]):
                if any([treenum in ['C23'] for treenum in treenums]):
                    bound = False
                return ('Symptom', bound)

            elif any([treenum.startswith('C16.320') for treenum in treenums]):
                if any([treenum in ['C16.320'] for treenum in treenums]):
                    bound = False
                return ('GeneticCondition', bound)

            elif any([treenum.startswith('C') for treenum in treenums]) and not any([treenum.startswith('C23') for treenum in treenums]):
                if any([treenum in ['C'] for treenum in treenums]):
                    bound = False
                return ('Disease', bound)

            else:
                return (None, False)
            
            
    def __create_database(self):
        mesh = pd.read_table(self.source_file)

        term_dict = dict()
        for index, row in mesh.iterrows():
            if row['id'] in term_dict:
                term_dict[row['id']]['treenums'].append(row['node'])
            else:
                term_dict[row['id']] = {'term':row['MeSH_term'], 'treenums':[row['node']]}
                
        # connect to database
        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        # create mesh table
        try:
            c.execute('DROP TABLE IF EXISTS mesh')
            c.execute("""CREATE TABLE mesh (
                            mesh_ui VARCHAR(7) PRIMARY KEY,
                            term VARCHAR(255),
                            entity VARCHAR(20),
                            bound INTEGER)
                      """)


            for k,v in term_dict.items():
                (entity, bound) = self.treenums2entity(v['treenums'])
                query = 'INSERT INTO mesh (mesh_ui, term, entity, bound) VALUES (?, ?, ?, ?)'
                c.execute(query, (k, v['term'], entity, int(bound)))
        except Exception as inst:
            print(inst)

        conn.commit()
        conn.close()