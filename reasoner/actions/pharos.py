import json
from urllib.request import urlopen
from urllib.parse import quote
from .action import Action


class JsonApiAction(Action):

    def __init__(self, precondition, effect):
        super().__init__(precondition, effect)


    def parse_request(self, url):
        with urlopen(url) as response:
           res = response.read().decode()
        return json.loads(res)




class PharosDrugToTarget(JsonApiAction):

    def __init__(self):
        super().__init__(['bound(Drug)'],['bound(Target) and connected(Drug, Target)'])


    def execute(self, query):
        drug = query['Drug']
        response = self.parse_request('https://pharos.nih.gov/idg/api/v1/ligands/search?q='+quote(drug))
        content = response['content']
        targets = []
        for entry in content:
            if entry['name'].lower() == drug.lower():
                links_url = entry['_links']['href']
                links = self.parse_request(links_url)
                for link in links:
                    if link['kind'] == 'ix.idg.models.Target':
                        targets.append({'Target': self.link_to_target(link)})

        return(targets)

    def find_property(self, label, properties):
        for prop in properties:
            if prop['label'] == label:
                return prop
        return None


    def link_to_target(self, link):

        target = ''
        target_prop = self.find_property('IDG Target',link['properties'])
        if target_prop != None:
            target = target_prop['term']

        activity_value = ''
        activity_term = ''
        target_prop = self.find_property('Ligand Activity',link['properties'])
        if target_prop != None:
            activity_term = target_prop['term']
            activity_value = self.find_property(activity_term,link['properties'])['numval']

        return [{'node':{'name':target, 'id':link['refid'], 'authority': 'Pharos:Target', 'URI':link['href']},'edge':{'p'+activity_term: activity_value}}]


class PharosTargetToDisease(JsonApiAction):

    def __init__(self):
        super().__init__(['bound(Target)'],['bound(Disease)', 'connected(Target, Pathway) and connected(Pathway, Cell) and connected(Cell, Symptom) and connected(Symptom, Disease)'])


    def execute(self, query):
        target = query['Target']
        response = self.parse_request('https://pharos.nih.gov/idg/api/v1/targets/search?q='+quote(target))
        content = response['content']
        if len(content) != 1:
            print("WARNING: Target not unique: "+target)
            return []
        links_url = content[0]['_links']['href']
        print(links_url)
        disease_list = []
        links = self.parse_request(links_url)
        for link in links:
            if link['kind'] == 'ix.idg.models.Disease':
                disease = self.link_to_disease(link)
                if disease != None:
                    disease_list.append(disease)
        return disease_list


    def link_to_disease(self, link):
        properties = link['properties']
        disease_name = self.get_property(properties,'IDG Disease')
        if disease_name == None:
            return None
        disease_node = {'name': disease_name}
        source = self.get_property(properties,'Data Source')
        if source != None:
            disease_node['source']=source
        disease_edge = {}
        for prop in properties:
            if 'label' in prop and 'numval' in prop:
                disease_edge[prop['label']]=prop['numval']

        return {'Disease':[{'node': disease_node,'edge':disease_edge}]}


    def get_property(seld, properties,property):
        for prop in properties:
            if prop['label'] == property:
                return prop['term']
        return None


class PharosTargetToPathway(JsonApiAction):

    def __init__(self):
        super().__init__(['bound(Target)'],['bound(Pathway)', 'connected(Target, Pathway)'])

    def execute(self, query):
        target = query['Target']
        response = self.parse_request('https://pharos.nih.gov/idg/api/v1/targets/search?q='+quote(target))
        content = response['content']
        if len(content) != 1:
            print("WARNING: Target not unique: "+target)
            return []
        properties_url = content[0]['_properties']['href']
        print(properties_url)
        pathway_list = []
        properties = self.parse_request(properties_url+'(label=*Pathway*)')
        for property in properties:
            pathway = self.property_to_pathway(property)
            if pathway != None:
                pathway_list.append(pathway)
        return pathway_list


    def property_to_pathway(self, property):
        if 'label' in property and 'term' in property:
            node = {}
            node['name'] = property['term']
            node['source'] = property['label']
            if 'href' in property and property['href'] != None:
                node['URI'] = property['href']
            return {'Pathway':[{'edge':{}, 'node':node}]}
        return None


class PharosTargetToTissue(JsonApiAction):

    def __init__(self):
        super().__init__(['bound(Target)'],['bound(Cell)', 'connected(Target, Pathway) and connected(Pathway, Cell)'])


    def execute(self, query):
        target = query['Target']
        response = self.parse_request('https://pharos.nih.gov/idg/api/v1/targets/search?q='+quote(target))
        content = response['content']
        if len(content) != 1:
            print("WARNING: Target not unique: "+target)
            return []
        links_url = content[0]['_links']['href']
        print(links_url)
        tissue_list = []
        links = self.parse_request(links_url+'(kind=ix.idg.models.Expression)')
        for link in links:
            tissue = self.link_to_tissue(link)
            if tissue != None:
                tissue_list.append(tissue)
        return tissue_list


    def link_to_tissue(self, link):
        properties = link['properties']
        edge = {}
        if 'href' in link:
            edge['href'] = link['href']
        for property in properties:
            if 'label' in property and 'term' in property:
                node = {}
                node['name'] = property['term']
                node['source'] = property['label']
                if 'href' in property and property['href'] != None:
                    node['URI'] = property['href']
                return {'Cell':[{'node': node,'edge':edge}]}
        return None




