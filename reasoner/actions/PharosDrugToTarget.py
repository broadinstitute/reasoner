import json
from urllib.request import urlopen
from urllib.parse import quote
from reasoner.actions.Action import Action


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
