import urllib.request, urllib.parse
import json
import xmltodict
from .action import Action
import xml.etree.ElementTree as etree

class EutilitiesAction(Action):
    def __init__(self, precondition, effect):
        super().__init__(precondition, effect)
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
    
    def esearch(self, term, db, retmax = 20, retmode = "json", quote = True):
        if quote == True:
            term = urllib.parse.quote_plus(term)
        query = 'esearch.fcgi?db=' + db +'&term=' + term + '&retmode=' + retmode +'&retmax=' + str(retmax)
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
    
    def add_quotation_marks(self, query):
        return '"%s"' % query


class ClinvarDiseaseToCondition(EutilitiesAction):
    
    def __init__(self):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)',
        'bound(Variant) and connected(Disease, Variant) and bound(Condition) and connected(Variant, Condition)'
        ]) 
    
    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Disease'])+' [dis]', 'clinvar')
        if len(search_results['esearchresult']['idlist']) == 0:
          return {}
        
        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.parse_request(self.efetch(uid, 'clinvar', rettype='variation'))
        variants = self.load_variants(fetch_result)
        result = self.find_disease(variants, query['Disease'])
        return(result)

    def parse_request(self, obj):
        root = etree.fromstring(obj)
        return root
    
    def find_disease(self, variants, query_term):
        for variant in variants:
            if 'Condition' not in variant.keys():
                continue
            remove_idx = list()
            for i in range(len(variant['Condition'])):
                if query_term in variant['Condition'][i]['node']['name'].lower():
                    variant['Variant'][0]['edge'] = variant['Condition'][i]['edge']
                    remove_idx.append(i)
            variant['Condition'] = [x for i,x in enumerate(variant['Condition']) if i not in remove_idx]
        return(variants)
    
    def parse_conditions(self, germline_elem):
        conditions = []
        for phenotype_elem in germline_elem.findall('./PhenotypeList/Phenotype'):
            condition = {'node':{'name':phenotype_elem.attrib['Name']},'edge':{}}
            for xref_elem in phenotype_elem.findall('./XRefList/XRef'):
                if 'id' not in condition['node'] or xref_elem.attrib['DB']=='MedGen':
                    condition['node']['id'] = xref_elem.attrib['ID']
                    condition['node']['authority'] = xref_elem.attrib['DB']
            if germline_elem.find('ReviewStatus') != None:
                condition['edge']['review_status'] = germline_elem.find('ReviewStatus').text
            if germline_elem.find('./ClinicalSignificance/Description')  != None:
                condition['edge']['clinical_significance'] = germline_elem.find('./ClinicalSignificance/Description').text
                if germline_elem.find('./ClinicalSignificance/Citation/ID') != None:
                    condition['edge']['pmid'] = germline_elem.find('./ClinicalSignificance/Citation/ID').text
            if condition['node']['name'] != 'not specified' and condition['node']['name'] != 'not provided' :
                conditions.append(condition)
        return conditions


    def parse_gene(self, gene_elem):
        gene = {}
        gene['node'] = {'id':gene_elem.attrib['GeneID'],'name':gene_elem.attrib['Symbol'], 'authority':'Entrez:GeneID'}
        gene['edge'] = {'relationship': gene_elem.attrib['RelationshipType']}
        return gene


    def parse_variant(self, variant_elem):

        variant_name = variant_elem.attrib['VariationName']
        variant_id = variant_elem.attrib['VariationID']
        variant = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}

        genes = [self.parse_gene(gene_elem) for gene_elem in variant_elem.findall('./GeneList/Gene')]
        if len(genes) > 0:
            variant['Gene'] = genes

        conditions = []
        for germline_elem in variant_elem.findall('./ClinicalAssertionList/GermlineList/Germline'):
            conditions.extend(self.parse_conditions(germline_elem))
        if len(conditions) > 0:
            variant['Condition'] = conditions
        return variant


    def load_variants(self, root):
        return [self.parse_variant(child) for child in root.findall('./VariationReport')]
    


class MeshConditionToGeneticCondition(EutilitiesAction):
    
    def __init__(self):
        super().__init__(['bound(Condition)', 'bound(Variant)', 'connected(Variant, Condition)'],['bound(GeneticCondition)', 'connected(Variant, GeneticCondition)'])
    
    def execute(self, query):
        search_results = self.esearch(query['Condition'], 'mesh')
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}
        
        uid = ','.join(search_results['esearchresult']['idlist'])
        summary = self.esummary(uid, 'mesh')
        
        genetic_conditions = list()
        for uid in summary['result']['uids']:
            entry = summary['result'][uid]
            treenums = [x['treenum'] for x in entry['ds_idxlinks']]
            term = entry['ds_meshterms'][0]
            mesh_id = entry['ds_meshui']
            if any([x.startswith('C16.320') for x in treenums]):
                genetic_conditions.append({'GeneticCondition':[{'node':{'name':query['Condition'], 'mesh_term':term, 'uid':uid, 'mesh_id':mesh_id}, 'edge':{}}]})

        return(genetic_conditions)
    
class MedGenConditionToGeneticCondition(EutilitiesAction):
    
    def __init__(self):
        super().__init__(['bound(Condition)', 'bound(Variant)', 'connected(Variant, Condition)'],['bound(GeneticCondition)', 'connected(Variant, GeneticCondition)'])
    
    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Condition']) + '[ExactTitle]', 'medgen')
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}
        
        uid = ','.join(search_results['esearchresult']['idlist'])
        summary = self.esummary(uid, 'medgen')
        
        genetic_conditions = list()
        for uid in summary['result']['uids']:
            entry = summary['result'][uid]
            if entry['title'] == query['Condition']:
                genetic_conditions.append({'GeneticCondition':[{'node':{'name':entry['title'], 'uid':uid, 'medgen_cid':entry['conceptid']}, 'edge':{}}]})
        
        return(genetic_conditions)
    