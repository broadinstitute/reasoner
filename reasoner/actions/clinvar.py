from .action import Action

import json
import xml.etree.ElementTree as etree
from urllib.request import urlopen
from urllib.parse import quote
import urllib.request, urllib.parse

class XmlApiAction(Action):

    def __init__(self, precondition, effect):
        super().__init__(precondition, effect)


    def parse_request(self, url):
        with urlopen(url) as response:
            tree = etree.parse(response)
            root = tree.getroot()
            return root

EUTILS_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

class ClinVarDiseaseToVariant(XmlApiAction):


    def __init__(self):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)',
        'bound(Variant) and connected(Disease, Variant) and bound(Condition) and connected(Variant, Condition)'
        ])


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
                condition['edge']['clinical_significace'] = germline_elem.find('./ClinicalSignificance/Description').text
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
            if len(genes) == 1:
                variant['Variant'][0]['node']['symbol'] = genes[0]['node']['name']

        conditions = []
        for germline_elem in variant_elem.findall('./ClinicalAssertionList/GermlineList/Germline'):
            conditions.extend(self.parse_conditions(germline_elem))
        if len(conditions) > 0:
            variant['Condition'] = conditions
        return variant


    def load_variants(self, id_list):
        root = self.parse_request(EUTILS_URL+'efetch.fcgi?db=clinvar&rettype=variation&id='+','.join(id_list))
        return [self.parse_variant(child) for child in root.findall('./VariationReport')]


    def load_page(self, url, ret_start, ret_max):
        root = self.parse_request(url+'&retmax='+str(ret_max)+'&retstart='+str(ret_start))
        count_elem = root.find('Count')
        count_value = int(count_elem.text)
        ret_max_elem = root.find('RetMax')
        ret_max_value = int(ret_max_elem.text)
        ret_start_elem = root.find('RetStart')
        ret_start_value = int(ret_start_elem.text)
        id_list = [id.text for id in root.find('IdList').findall('Id')]
        variants = self.load_variants(id_list)
        return {'count':count_value, 'retmax':ret_max_value, 'retstart':ret_start_value, 'ids':id_list, 'variants': variants}


    def execute(self, query):
        disease = query['Disease']
        variants = []
        page_start = 0
        done = False
        while not done:
            page = self.load_page(EUTILS_URL+'esearch.fcgi?db=clinvar&term='+quote(disease)+'[dis]',page_start,20)
            variants.extend(page['variants'])
            page_start = page['retstart'] + page['retmax']
            done = page_start >= page['count']
        return variants


class ClinVarDiseaseToConditionOld(XmlApiAction):


    def __init__(self):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant) and bound(ClinicalSignificance) and connected(Variant, ClinicalSignificance) and bound(Condition) and connected(ClinicalSignificance, Condition)',
         'bound(Variant) and connected(Disease, Variant) and bound(ClinicalSignificance) and connected(Variant, ClinicalSignificance) and bound(Condition) and connected(ClinicalSignificance, Condition) and bound(Gene) and connected(Variant, Gene)'
        ])

    def parse_gene(self, gene_elem):
        gene = {}
        gene['node'] = {'id':gene_elem.attrib['GeneID'],'name':gene_elem.attrib['Symbol'], 'authority':'Entrez:GeneID'}
        gene['edge'] = {'relationship': gene_elem.attrib['RelationshipType']}
        return gene

    def parse_conditions(self, germline_elem):
        conditions = []
        for phenotype_elem in germline_elem.findall('./PhenotypeList/Phenotype'):
            condition = {'node':{'name':phenotype_elem.attrib['Name']},'edge':{}}
            for xref_elem in phenotype_elem.findall('./XRefList/XRef'):
                if 'id' not in condition['node'] or xref_elem.attrib['DB']=='MedGen':
                    condition['node']['id'] = xref_elem.attrib['ID']
                    condition['node']['authority'] = xref_elem.attrib['DB']
            clin_sign = {'node':{}, 'edge':{}}
            if germline_elem.find('ReviewStatus') != None:
                clin_sign['node']['review_status'] = germline_elem.find('ReviewStatus').text
            if germline_elem.find('./ClinicalSignificance/Description')  != None:
                clin_sign['node']['name'] = germline_elem.find('./ClinicalSignificance/Description').text
                if germline_elem.find('./ClinicalSignificance/Citation/ID') != None:
                    condition['edge']['pmid'] = germline_elem.find('./ClinicalSignificance/Citation/ID').text
            if condition['node']['name'] != 'not specified' and condition['node']['name'] != 'not provided' and 'name' in clin_sign['node']:
                conditions.append({'Condition':[condition],'ClinicalSignificance':[clin_sign]})
        return conditions

    def parse_variant(self, variant_elem):

        variant_name = variant_elem.attrib['VariationName']
        variant_id = variant_elem.attrib['VariationID']
        variant = [{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]

        genes = [self.parse_gene(gene_elem) for gene_elem in variant_elem.findall('./GeneList/Gene')]
        if len(genes) == 1:
            variant[0]['node']['symbol'] = genes[0]['node']['name']

        conditions = []
        for germline_elem in variant_elem.findall('./ClinicalAssertionList/GermlineList/Germline'):
            conditions.extend(self.parse_conditions(germline_elem))
        for condition in conditions:
            condition['Variant']=variant
            if len(genes) > 0:
                condition['Gene'] = genes
        return conditions


    def load_variants(self, id_list):
        root = self.parse_request(EUTILS_URL+'efetch.fcgi?db=clinvar&rettype=variation&id='+','.join(id_list))
        variants = []
        for child in root.findall('./VariationReport'):
            variants.extend(self.parse_variant(child))
        return variants

    def load_page(self, url, ret_start, ret_max):
        root = self.parse_request(url+'&retmax='+str(ret_max)+'&retstart='+str(ret_start))
        count_elem = root.find('Count')
        count_value = int(count_elem.text)
        ret_max_elem = root.find('RetMax')
        ret_max_value = int(ret_max_elem.text)
        ret_start_elem = root.find('RetStart')
        ret_start_value = int(ret_start_elem.text)
        id_list = [id.text for id in root.find('IdList').findall('Id')]
        variants = self.load_variants(id_list)
        return {'count':count_value, 'retmax':ret_max_value, 'retstart':ret_start_value, 'ids':id_list, 'variants': variants}


    def execute(self, query):
        disease = query['Disease']
        variants = []
        page_start = 0
        done = False
        while not done:
            page = self.load_page(EUTILS_URL+'esearch.fcgi?db=clinvar&term='+quote(disease)+'[dis]',page_start,20)
            variants.extend(page['variants'])
            page_start = page['retstart'] + page['retmax']
            done = page_start >= page['count']
        return variants



class ClinvarActionBad(Action):
    def __init__(self, precondition, effect, additional_term=''):
        super().__init__(precondition, effect)
        self.additional_term = additional_term

    def load_variants(self, result):
        return [self.parse_variant(id, result[id]) for id in result['uids']]

    def parse_gene(self, variation_set, gene_dict):
        if 'symbol' in gene_dict:
            node = {'name':gene_dict['symbol']}
            if 'geneid' in gene_dict:
                node['id'] = gene_dict['geneid']
                node['authority'] = 'Entrez:GeneID'
            edge = {}
            if 'variant_type' in variation_set[0]:
                edge['relationship'] = variation_set[0]['variant_type']
            return {'node': node, 'edge':edge}
        return None


    def load_conditions(self, rcvs):
        conditions = []
        result_set = self.parse_xml(self.efetch(','.join(rcvs),'clinvar',rettype='clinvarset'))
        for clin_var_set in result_set.findall('./ClinVarSet'):
            for assertion_elem in clin_var_set.findall('./ReferenceClinVarAssertion'):
                conditions.extend(self.parse_conditions(assertion_elem))

        return conditions


    def parse_conditions(self, assertion_elem):
        conditions = []
        edge = {}
        if assertion_elem.find('./ClinicalSignificance/Description') != None:
            edge['clinical_significance']=assertion_elem.find('./ClinicalSignificance/Description').text
        if assertion_elem.find('./ClinicalSignificance/ReviewStatus') != None:
            edge['review_status']=assertion_elem.find('./ClinicalSignificance/ReviewStatus').text

        for trait_elem in assertion_elem.findall('./TraitSet/Trait'):
            if trait_elem.attrib['Type'] == 'Disease':
                node = self.parse_disease(trait_elem)
                if node != None and node['name'] != 'not specified' and node['name'] != 'not provided':
                    conditions.append({'node':node, 'edge':edge})

        return conditions


    def parse_disease(self, trait_elem):
        if trait_elem.find('./Name/ElementValue') == None:
            return None
        node = {'name': trait_elem.find('./Name/ElementValue').text}
        for xref_elem in trait_elem.findall('./XRef'):
            if 'id' not in node or xref_elem.attrib['DB']=='MedGen':
                node['id'] = xref_elem.attrib['ID']
                node['authority'] = xref_elem.attrib['DB']

        return node


    def find_disease(self, variants, query_term):
        for variant in variants:
            if 'Condition' not in variant.keys():
                continue
            remove_idx = list()
            for i in range(len(variant['Condition'])):
                if query_term.lower() in variant['Condition'][i]['node']['name'].lower():
                    variant['Variant'][0]['edge'] = variant['Condition'][i]['edge']
                    remove_idx.append(i)
            variant['Condition'] = [x for i,x in enumerate(variant['Condition']) if i not in remove_idx]
        return(variants)

class ClinvarDiseaseToConditionBad(ClinvarActionBad):
    """Find a all conditions connected to a disease via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = '+protective'):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)',
        'bound(Variant) and connected(Disease, Variant) and bound(Condition) and connected(Variant, Condition)'
        ],
        additional_search_term)


    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Disease'])+' [dis]'+self.additional_term, 'clinvar', retmax = 200)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.esummary(uid, 'clinvar')['result']
        variants = self.load_variants(fetch_result)
        result = self.find_disease(variants, query['Disease'])
        return result



    def parse_variant(self, variant_id, variant_in):
        variant_name = variant_in['title']
        genes = []
        for gene in variant_in['genes']:
            if self.parse_gene(variant_in['variation_set'], gene) != None:
                genes.append(self.parse_gene(variant_in['variation_set'], gene))
        conditions = self.load_conditions(variant_in['supporting_submissions']['rcv'])

        variant_out = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}
        if len(genes) > 0:
            variant_out['Gene'] = genes
            if len(genes) == 1:
                variant_out['Variant'][0]['node']['symbol'] = genes[0]['node']['name']
        if len(conditions) > 0:
            variant_out['Condition'] = conditions

        return variant_out




class ClinvarDiseaseToGeneBad(ClinvarActionBad):
    """Find a all conditions connected to a disease via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = '+protective'):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)'
        ],
        additional_search_term)

    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Disease'])+' [dis]'+self.additional_term, 'clinvar', retmax = 200)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.esummary(uid, 'clinvar')['result']
        variants = self.load_variants(fetch_result)
        return variants


    def parse_variant(self, variant_id, variant_in):
        variant_name = variant_in['title']
        genes = []
        for gene in variant_in['genes']:
            if self.parse_gene(variant_in['variation_set'], gene) != None:
                genes.append(self.parse_gene(variant_in['variation_set'], gene))

        variant_out = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}
        if len(genes) > 0:
            variant_out['Gene'] = genes
            if len(genes) == 1:
                variant_out['Variant'][0]['node']['symbol'] = genes[0]['node']['name']

        return variant_out



class ClinvarGeneToConditionBad(ClinvarActionBad):
    """Find a all conditions connected to a gene via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = ' and (("clinsig pathogenic"[Properties]) OR ("clinsig likely pathogenic"[Properties]) OR ("clinsig risk factor"[Properties]))'):
        super().__init__(['bound(Gene)'],
        ['bound(Variant) and connected(Gene, Variant)',
        'bound(Variant) and connected(Gene, Variant) and bound(Condition) and connected(Variant, Condition)'
        ],
        additional_search_term)


    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Gene'])+'[gene]'+self.additional_term, 'clinvar', retmax = 200)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.esummary(uid, 'clinvar')['result']
        variants = self.load_variants(fetch_result)
        return variants

    def parse_variant(self, variant_id, variant_in):
        variant_name = variant_in['title']
        genes = []
        for gene in variant_in['genes']:
            if self.parse_gene(variant_in['variation_set'], gene) != None:
                genes.append(self.parse_gene(variant_in['variation_set'], gene))
        conditions = self.load_conditions(variant_in['supporting_submissions']['rcv'])

        variant_out = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}
        if len(genes) == 1:
            variant_out['Variant'][0]['node']['symbol'] = genes[0]['node']['name']
        if len(conditions) > 0:
            variant_out['Condition'] = conditions

        return variant_out

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
        return etree.fromstring(obj)

    def esearch(self, term, db, retstart = 0, retmax = 20, retmode = "json", quote = True, sort = None, count = False):
        if quote == True:
            term = urllib.parse.quote_plus(term)
        query = 'esearch.fcgi?db=' + db +'&term=' + term + '&retmode=' + retmode + '&retstart=' + str(retstart) + '&retmax=' + str(retmax)

        if sort is not None:
            query = query + '&sort=' + sort
        if count == True:
            query = query + '&rettype=count'

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
        print(url)
        with urllib.request.urlopen(url) as response:
            res = response.read()
        return res

    def add_quotation_marks(self, query):
        return '"%s"' % query


class ClinvarAction(EutilitiesAction):
    def __init__(self, precondition, effect, additional_term=''):
        super().__init__(precondition, effect)
        self.additional_term = additional_term

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


    def load_variants(self, root):
        variants = []
        for child in root.findall('./VariationReport'):
            variant = self.parse_variant(child)
            if variant != None:
                variants.append(variant)
        return variants


class ClinvarDiseaseToCondition(ClinvarAction):
    """Find a all conditions connected to a disease via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = '+protective'):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)',
        'bound(Variant) and connected(Disease, Variant) and bound(Condition) and connected(Variant, Condition)'
        ],
        additional_search_term)

    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Disease'])+'[dis]'+self.additional_term, 'clinvar', retmax = 500)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.parse_xml(self.efetch(uid, 'clinvar', rettype='variation'))
        variants = self.load_variants(fetch_result)
        result = self.find_disease(variants, query['Disease'])
        return result


    def parse_variant(self, variant_elem):

        variant_name = variant_elem.attrib['VariationName']
        variant_id = variant_elem.attrib['VariationID']
        variant = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}

        genes = [self.parse_gene(gene_elem) for gene_elem in variant_elem.findall('./GeneList/Gene')]
        if len(genes) > 0:
            variant['Gene'] = genes
            if len(genes) == 1:
                variant['Variant'][0]['node']['symbol'] = genes[0]['node']['name']

        conditions = []
        for germline_elem in variant_elem.findall('./ClinicalAssertionList/GermlineList/Germline'):
            conditions.extend(self.parse_conditions(germline_elem))
        if len(conditions) > 0:
            variant['Condition'] = conditions
        return variant



class ClinvarDiseaseToGene(ClinvarAction):
    """Find a all conditions connected to a disease via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = '+protective'):
        super().__init__(['bound(Disease)'],
        ['bound(Variant) and connected(Disease, Variant)',
        'bound(Variant) and connected(Disease, Variant) and bound(Gene) and connected(Variant, Gene)'
        ],
        additional_search_term)

    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Disease'])+'[dis]'+self.additional_term, 'clinvar', retmax = 500)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.parse_xml(self.efetch(uid, 'clinvar', rettype='variation'))
        variants = self.load_variants(fetch_result)
        return variants


    def parse_variant(self, variant_elem):

        variant_name = variant_elem.attrib['VariationName']
        variant_id = variant_elem.attrib['VariationID']
        variant = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}

        genes = [self.parse_gene(gene_elem) for gene_elem in variant_elem.findall('./GeneList/Gene')]
        if len(genes) > 0:
            variant['Gene'] = genes
            if len(genes) == 1:
                variant['Variant'][0]['node']['symbol'] = genes[0]['node']['name']

        return variant


class ClinvarGeneToCondition(ClinvarAction):
    """Find a all conditions connected to a gene via a common variant in ClinVar.
    """
    def __init__(self, additional_search_term = ' and (("clinsig pathogenic"[Properties]) OR ("clinsig likely pathogenic"[Properties]) OR ("clinsig risk factor"[Properties]))'):
        super().__init__(['bound(Gene)'],
        ['bound(Variant) and connected(Gene, Variant) and bound(Condition) and connected(Variant, Condition)'
        ],
        additional_search_term)


    def execute(self, query):
        search_results = self.esearch(self.add_quotation_marks(query['Gene'])+'[gene]'+self.additional_term, 'clinvar', retmax = 500)
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}

        uid = ','.join(search_results['esearchresult']['idlist'])
        fetch_result = self.parse_xml(self.efetch(uid, 'clinvar', rettype='variation'))
        variants = self.load_variants(fetch_result)
        return variants


    def parse_variant(self, variant_elem):

        variant_name = variant_elem.attrib['VariationName']
        variant_id = variant_elem.attrib['VariationID']
        variant = {'Variant':[{'node':{'id':variant_id,'name':variant_name, 'authority':'ClinVar:VariationID'},'edge':{}}]}

        conditions = []
        for germline_elem in variant_elem.findall('./ClinicalAssertionList/GermlineList/Germline'):
            conditions.extend(self.parse_conditions(germline_elem))
        if len(conditions) == 0:
            return None
        variant['Condition'] = conditions

        genes = [self.parse_gene(gene_elem) for gene_elem in variant_elem.findall('./GeneList/Gene')]
        if len(genes) == 1:
            variant['Variant'][0]['node']['symbol'] = genes[0]['node']['name']

        return variant


