from .Action import Action
import urllib.request, urllib.parse
import json
import xmltodict
import pandas as pd
import dateutil.parser

class PubmedQuery(Action):
  def __init__(self, precondition_entities, effect_entities):
    super().__init__(precondition_entities, effect_entities)
    self.url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    self.mesh_terms = pd.read_table('../../data/MeSH_hierarchy.txt')
    
  def get_request(self, url):
    with urllib.request.urlopen(url) as response:
       res = response.read().decode()
    return res

  def parse_request(self, url):
    with urllib.request.urlopen(url) as response:
       res = response.read().decode()
    return json.loads(res)
  
  def search_pubmed(self, term):
    query = 'esearch.fcgi?db=pubmed&term=' + term + '&sort=relevance&retmode=json'
    res = self.parse_request(self.url_prefix + query)
    return(res)
  
  def get_article_count(self, term):
    query = 'esearch.fcgi?db=pubmed&term=' + term + '&rettype=count&retmode=json'
    res = self.parse_request(self.url_prefix + query)
    return(int(res['esearchresult']['count']))
  
  def get_uid_subset(self, term, start = 0, n = None):
    if n is None: 
      query = 'esearch.fcgi?db=pubmed&term=' + term + '&sort=most+recent&retmode=json&retstart=' + str(start)
    else:
      query = 'esearch.fcgi?db=pubmed&term=' + term + '&sort=most+recent&retmode=json&retstart=' + str(start) + '&retmax=' + str(n)
    res = self.parse_request(self.url_prefix + query)
    return(res['esearchresult']['idlist'])
  
  def get_summary(self, entry_id):
    query = 'esummary.fcgi?db=pubmed&id=' + entry_id + '&retmode=json'
    res = self.parse_request(self.url_prefix + query)
    return(res)
    
  def get_oldest_article_date(self, term):
    count = self.get_article_count(term)
    uid = self.get_uid_subset(term, count-1)[-1]
    summary = self.get_summary(uid)
    return(dateutil.parser.parse(summary['result'][uid]['pubdate']))
    
  def get_article_list(self, term):
    result = self.search_pubmed(term)
    return(result['esearchresult']['idlist'])
  
  def fetch_pubmed(self, entry_id):
    query = 'efetch.fcgi?db=pubmed&id=' + entry_id + '&retmode=xml'
    res = self.get_request(self.url_prefix + query)
    return(res)

  def get_article_set_mesh_terms(self, article_ids):
    req = ','.join(article_ids)
    res = self.fetch_pubmed(req)
    doc = xmltodict.parse(res)
    mesh_list = list()
    for article in doc['PubmedArticleSet']['PubmedArticle']:
        if 'MeshHeadingList' in article['MedlineCitation']:
            for mh in article['MedlineCitation']['MeshHeadingList']['MeshHeading']:
                mesh_list.append(mh['DescriptorName']['#text'])
    return(mesh_list)

  def get_article_mesh_terms(self, article_id):
    req = article_id
    res = self.fetch_pubmed(req)
    doc = xmltodict.parse(res)
    if 'MeshHeadingList' in doc['PubmedArticleSet']['PubmedArticle']['MedlineCitation']:
        return [mh['DescriptorName']['#text'] for mh in doc['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['MeshHeadingList']['MeshHeading']]
    else:
        return([])

  def search_mesh(self, term):
    query = 'esearch.fcgi?db=mesh&term=' + urllib.parse.quote_plus(term) + '&retmode=json'
    res = self.parse_request(self.url_prefix + query)
    return(res)
  
  def generate_query_string(self, terms, mesh = True):
    if mesh:
        query_list = [term + ' [MeSH Term]' for term in terms]
    else:
        query_list = terms
    query = ' '.join(query_list).replace(' ', '+')
    return(query)
  
  def get_term_type(self, term):
    node_list = self.mesh_terms[(self.mesh_terms.MeSH_term == term)].node.tolist()
    if any(node.startswith('D02') for node in node_list):
      return('Drug')
    elif any(node.startswith('D12.776') for node in node_list) or any(node.startswith('D08.811') for node in node_list):
      return('Target')
    elif any(node.startswith('G03.493') for node in node_list) or any(node.startswith('G04.835') for node in node_list):
      return('Pathway')
    elif any(node.startswith('A11') for node in node_list):
      return('Cell')
    elif any(node.startswith('C23') for node in node_list):
      return('Phenotype')
    elif any(node.startswith('C') for node in node_list) and not any(node.startswith('C23') for node in node_list):
      return('Disease')
    else:
      return(None)
  
  def run_query(self, query_tuple, mesh = True):
    query_string = self.generate_query_string(query_tuple, mesh)
    article_list = self.get_article_list(query_string)
    mesh_lists = {article:self.get_article_mesh_terms(article) for article in article_list}

    nodes = list()
    for key,value in mesh_lists.items():
      term_dict = dict()
      for term in value:
        term_type = self.get_term_type(term)
        if term_type is not None:
          if term_type in term_dict.keys():
            term_dict[term_type].append({'node':{'name':term}, 'edge':{}})
          else:
            term_dict[term_type] = [{'node':{'name':term}, 'edge':{}}]
      nodes.append(term_dict)
    return(nodes)
  
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



class PubmedDrugDiseasePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Disease)'], ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Phenotype) and connected(Phenotype, Disease)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Disease'], {'Target', 'Pathway', 'Cell', 'Phenotype'}))
    

class PubmedDrugPhenotypePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Phenotype)'], ['bound(Target)', 'bound(Pathway)', 'bound(Cell)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Phenotype)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Phenotype'], {'Target', 'Pathway', 'Cell'}))
    

class PubmedDrugCellPath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Cell)'], ['bound(Target)', 'bound(Pathway)', 'connected(Drug, Target) and connected(Target, Pathway) and connected(Pathway, Cell)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Cell'], {'Target', 'Pathway'}))
    
    
class PubmedDrugPathwayPath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Drug)', 'bound(Pathway)'], ['bound(Target)', 'connected(Drug, Target) and connected(Target, Pathway)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Drug'], query['Pathway'], {'Target'}))
    
    
    
class PubmedTargetDiseasePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Disease)'], ['bound(Pathway)', 'bound(Cell)', 'bound(Phenotype)', 'connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Phenotype) and connected(Phenotype, Disease)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Disease'], {'Pathway', 'Cell', 'Phenotype'}))
    
    
class PubmedTargetPhenotypePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Phenotype)'], ['bound(Pathway)', 'bound(Cell)', 'connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Phenotype)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Phenotype'], {'Pathway', 'Cell'}))
    
    
class PubmedTargetCellPath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Target)', 'bound(Cell)'], ['bound(Pathway)', 'connected(Target, Pathway) and connected(Pathway, Cell)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Target'], query['Cell'], {'Pathway'}))
    
    
class PubmedPathwayDiseasePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Pathway)', 'bound(Disease)'], ['bound(Cell)', 'bound(Phenotype)', 'connected(Pathway, Cell) and connected(Cell, Phenotype) and connected(Phenotype, Disease)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Pathway'], query['Disease'], {'Cell', 'Phenotype'}))
    
    
class PubmedPathwayPhenotypePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Pathway)', 'bound(Phenotype)'], ['bound(Cell)', 'connected(Pathway, Cell) and connected(Cell, Phenotype)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Pathway'], query['Phenotype'], {'Cell'}))
    
    
class PubmedCellDiseasePath(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Cell)', 'bound(Disease)'], ['bound(Phenotype)', 'connected(Cell, Phenotype) and connected(Phenotype, Disease)'])
    
    def execute(self, query):
        return(self.execute_path_query(query['Cell'], query['Disease'], {'Phenotype'}))
    
    
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
    
class PubmedDiseaseToPhenotype(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Disease)'], ['bound(Phenotype) and connected(Phenotype, Disease)'])
    
    def execute(self, query):
        return(self.execute_entity_query(query['Disease'], {'Phenotype'}))
    
class PubmedPhenotypeToCell(PubmedQuery):
    def __init__(self):
        super().__init__(['bound(Phenotype)'], ['bound(Cell) and connected(Cell, Phenotype)'])
    
    def execute(self, query):
        return(self.execute_entity_query(query['Phenotype'], {'Cell'}))