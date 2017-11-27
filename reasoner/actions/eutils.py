"""Actions to access NCBI E-Utilities.
"""

import json
import xmltodict
import xml.etree.ElementTree as etree
import dateutil.parser
import urllib.request, urllib.parse

from .action import Action
from ..MeshTools import MeshTools


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
        with urllib.request.urlopen(url) as response:
            res = response.read()
        return res
    
    def add_quotation_marks(self, query):
        return '"%s"' % query


class ClinvarDiseaseToCondition(EutilitiesAction):
    """Find a all conditions connected to a disease via a common variant in ClinVar.
    """
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
        fetch_result = self.parse_xml(self.efetch(uid, 'clinvar', rettype='variation'))
        variants = self.load_variants(fetch_result)
        result = self.find_disease(variants, query['Disease'])
        return result
    
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
    """Use MeSH to identify whether a condition has a genetic cause.
    """
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
    """Use MedGen to identify whether a condition has a genetic cause.
    """
    def __init__(self):
        super().__init__(['bound(Condition)', 'bound(Variant)', 'connected(Variant, Condition)'],['bound(GeneticCondition)', 'connected(Variant, GeneticCondition)'])
    
    def execute(self, query):
        """Uses MedGen to identify whether a given condition is genetic.
        
        Parameters
        ----------
        query : str
            name of condition
        
        Returns
        -------
        genetic_conditions : list
            A list of dicts, one for each identified genetic condition.
            Keys are returned entities ('GeneticCondition'), values are
            a 'node' and 'edge' dict, each of which contains attributes
            for the respective structure.
        
        """
        
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
    


class PubmedQuery(EutilitiesAction):
    def __init__(self, precondition, effect):
        super().__init__(precondition, effect)
        self.mesh_tools = MeshTools()
    
    def parse_mesh_heading(self, mh):
        desc = mh.find('DescriptorName')
        entity = self.mesh_tools.id2entity(desc.attrib['UI'])
        
        if entity[1] == False:
            return (None, {})
        else:
            qual = mh.find('QualifierName')
            major = desc.attrib['MajorTopicYN'] == 'Y'
            if qual is not None:
                 major = major or qual.attrib['MajorTopicYN'] == 'Y'
                
            term_dict = {'node':{'name':desc.text,
                                 'mesh:ui':desc.attrib['UI'],
                                 'major_topic':major},
                         'edge':{}
                        }
        return (entity[0], term_dict)

        
    def extract_mesh_terms(self, article):
        mesh_headings = dict()
        for mh in article.findall('./MedlineCitation/MeshHeadingList/MeshHeading'):
            (entity, term) = self.parse_mesh_heading(mh)
            
            if entity is None:
                continue
            
            if entity in mesh_headings:
                mesh_headings[entity].append(term)
            else:
                mesh_headings[entity] = [term]
        return mesh_headings      
    
    def generate_query_string(self, terms, mesh = True):
        if mesh:
            query_list = [term + ' [MeSH Term]' for term in terms]
        else:
            query_list = terms
        query = ' '.join(query_list).replace(' ', '+')
        return(query)

    def run_query(self, query_tuple, mesh = True):
        query_string = self.generate_query_string(query_tuple, mesh)
        search_results = self.esearch(query_string, 'pubmed', sort='relevance')
        if len(search_results['esearchresult']['idlist']) == 0:
            return {}
        
        uid = ','.join(search_results['esearchresult']['idlist'])
        
        article_xml = self.efetch(uid, 'pubmed', retmode="xml")
        root = self.parse_xml(article_xml)
        return [self.extract_mesh_terms(article) for article in root.findall('./PubmedArticle')]

    def filter_results(self, article_list, keep_variables):
        for article in article_list:
            remove_keys = set(article.keys()) - keep_variables
            for k in remove_keys:
                del article[k]
        return([article for article in article_list if article])

    def execute_path_query(self, start, end, keep_variables):
        article_list = self.run_query((start, end))
        return(self.filter_results(article_list, keep_variables))

    def execute_entity_query(self, entity, keep_variables, mesh = True):
        article_list = self.run_query((entity,), mesh)
        return(self.filter_results(article_list, keep_variables))

    def execute(self, query):
        pass



class PubmedEdgeStats(PubmedQuery):
    """Get connection statistics based on term cooccurence from PubMed.
    """
    def __init__(self):
        super().__init__([], [])

    def get_oldest_article_date(self, query, count = None):
        if count is None:
            count = self.get_article_count(query)
        search_results = self.esearch(query, 'pubmed', sort = 'most+recent', retstart = count-1)
        if len(search_results['esearchresult']['idlist']) == 0:
            return -1
        
        uid = search_results['esearchresult']['idlist'][-1]
        summary = self.esummary(uid, 'pubmed')
        #return(dateutil.parser.parse(summary['result'][uid]['pubdate']))
        return(int(summary['result'][uid]['pubdate'][0:4]))

    def get_article_count(self, query):
        search_results = self.esearch(query, 'pubmed', count = True)
        return(int(search_results['esearchresult']['count']))

    def get_edge_stats(self, start, end):
        query = self.generate_query_string((start, end))
        stats = dict()
        stats['article_count'] = self.get_article_count(query)
        
        if stats['article_count'] > 0:
            year_first_article = self.get_oldest_article_date(query, stats['article_count'])
            if not year_first_article == -1:
                stats['year_first_article'] = year_first_article
        return(stats)



class PubmedDrugDiseasePath(PubmedQuery):
    """Use PubMed to find a path between a drug and a disease.
    """
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Disease)'], ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom) and connected(Symptom, Disease)'])

    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Disease'], {'Target', 'Pathway', 'Cell', 'Symptom'}))


class PubmedDrugSymptomPath(PubmedQuery):
    """Use PubMed to find a path between a drug and a symptom.
    """
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Symptom)'], ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom)'])

    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Symptom'], {'Target', 'Pathway', 'Cell'}))


class PubmedDrugCellPath(PubmedQuery):
    """Use PubMed to find a path between a drug and a cell.
    """
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Cell)'], ['bound(Target)', 'bound(Pathway)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell)'])

    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Cell'], {'Target', 'Pathway'}))


class PubmedDrugPathwayPath(PubmedQuery):
    """Use PubMed to find a path between a drug and a pathway.
    """
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Pathway)'], ['bound(Target)', 'connected(Drug, Target) and connected(Target, Pathway)'])

    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Pathway'], {'Target'}))



class PubmedTargetDiseasePath(PubmedQuery):
    """Use PubMed to find a path between a target and a disease.
    """
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Disease)'], ['bound(Pathway)', 'bound(Cell)', 'bound(Symptom)', 'connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom) and connected(Symptom, Disease)'])

    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Disease'], {'Pathway', 'Cell', 'Symptom'}))


class PubmedTargetSymptomPath(PubmedQuery):
    """Use PubMed to find a path between a target and a symptom.
    """
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Symptom)'], ['bound(Pathway)', 'bound(Cell)', 'connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom)'])

    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Symptom'], {'Pathway', 'Cell'}))


class PubmedTargetCellPath(PubmedQuery):
    """Use PubMed to find a path between a target and a cell.
    """
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Cell)'], ['bound(Pathway)', 'connected(Target, Pathway) and connected(Pathway, Cell)'])

    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Cell'], {'Pathway'}))


class PubmedPathwayDiseasePath(PubmedQuery):
    """Use PubMed to find a path between a pathway and a disease.
    """
    def __init__(self):
        super().__init__(['bound(Pathway)', 'bound(Disease)'], ['bound(Cell)', 'bound(Symptom)', 'connected(Pathway, Cell) and connected(Cell, Symptom) and connected(Symptom, Disease)'])

    def execute(self, query):
        return(self.execute_path_query(query['Pathway'], query['Disease'], {'Cell', 'Symptom'}))


class PubmedPathwaySymptomPath(PubmedQuery):
    """Use PubMed to find a path between a pathway and a symptom.
    """
    def __init__(self):
        super().__init__(['bound(Pathway)', 'bound(Symptom)'], ['bound(Cell)', 'connected(Pathway, Cell) and connected(Cell, Symptom)'])

    def execute(self, query):
        return(self.execute_path_query(query['Pathway'], query['Symptom'], {'Cell'}))


class PubmedCellDiseasePath(PubmedQuery):
    """Use PubMed to find a path between a cell and a disease.
    """
    def __init__(self):
        super().__init__(['bound(Cell)', 'bound(Disease)'], ['bound(Symptom)', 'connected(Cell, Symptom) and connected(Symptom, Disease)'])

    def execute(self, query):
        return(self.execute_path_query(query['Cell'], query['Disease'], {'Symptom'}))


## simple node actions
class PubmedDrugToTarget(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Drug)'], ['bound(Target) and connected(Drug, Target)'])

    def execute(self, query):
        return(self.execute_entity_query(query['Drug'], {'Target'}))


class PubmedTargetToPathway(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Target)'], ['bound(Pathway) and connected(Target, Pathway)'])

    def execute(self, query):
        return(self.execute_entity_query(query['Target'], {'Pathway'}, mesh = False))

class PubmedPathwayToCell(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Pathway)'], ['bound(Cell) and connected(Pathway, Cell)'])

    def execute(self, query):
        return(self.execute_entity_query(query['Pathway'], {'Cell'}))

class PubmedDiseaseToSymptom(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Disease)'], ['bound(Symptom) and connected(Symptom, Disease)'])

    def execute(self, query):
        return(self.execute_entity_query(query['Disease'], {'Symptom'}))

class PubmedSymptomToCell(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Symptom)'], ['bound(Cell) and connected(Cell, Symptom)'])

    def execute(self, query):
        return(self.execute_entity_query(query['Symptom'], {'Cell'}))
