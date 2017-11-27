from .action import Action

import xml.etree.ElementTree as etree
from urllib.request import urlopen
from urllib.parse import quote


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


class ClinVarDiseaseToCondition(XmlApiAction):


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

