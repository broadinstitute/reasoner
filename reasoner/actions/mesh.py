import urllib.request, urllib.parse
import json
from .action import Action

class MeshConditionToGeneticCondition(Action):
    
    def __init__(self):
        super().__init__(['bound(Condition)'],['connected(Condition, GeneticCondition)'])
        self.url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    
    def parse_request(self, url):
        with urllib.request.urlopen(url) as response:
            res = response.read().decode()
        return json.loads(res)
    
    def esearch(self, term):
        query = 'esearch.fcgi?db=mesh&term=' + urllib.parse.quote_plus(term) + '&retmode=json'
        res = self.parse_request(self.url_prefix + query)
        return(res)
    
    def esummary(self, entry_id):
        query = 'esummary.fcgi?db=mesh&id=' + entry_id + '&retmode=json'
        res = self.parse_request(self.url_prefix + query)
        return(res)
    
    def execute(self, query):
        results = self.esearch(query['Condition'])
        if len(results['esearchresult']['idlist']) == 0:
          return {}
        
        uid = results['esearchresult']['idlist'][0]
        summary = self.esummary(uid)
        
        genetic_conditions = list()
        for uid in summary['result']['uids']:
            entry = summary['result'][uid]
            treenums = [x['treenum'] for x in entry['ds_idxlinks']]
            term = entry['ds_meshterms'][0]
            mesh_id = entry['ds_meshui']
            if any([x.startswith('C16.320') for x in treenums]):
                genetic_conditions.append({'GeneticCondition':[{'node':{'name':term, 'uid':uid, 'mesh_id':mesh_id}, 'edge':{}}]})

        return(genetic_conditions)