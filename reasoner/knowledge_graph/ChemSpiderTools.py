import requests
import json
from .Config import Config


class ChemSpiderTools:
    def __init__(self):
        config = Config().config
        self.base_url = 'https://api.rsc.org/compounds/v1/'
        self.apikey = config['chemspider']['apikey']

    def post(self, url, data):
        r = requests.post(url,
                          headers={'apikey': self.apikey},
                          data=json.dumps(data))
        if r.status_code == requests.codes.ok:
            return(r.json())
        else:
            return(None)

    def get(self, url, params=None):
        if params is None:
            r = requests.get(url, headers={'apikey': self.apikey})
        else:
            r = requests.get(url,
                             headers={'apikey': self.apikey},
                             params=params)
        if r.status_code == requests.codes.ok:
            return(r.json())
        else:
            return(None)

    def search_name(self, name):
        url = self.base_url + 'filter/name'
        r = self.post(url, {'name': name})
        return(self.get_results(r['queryId']))

    def get_results(self, query_id):
        url = self.base_url + 'filter/%s/results' % query_id
        r = self.get(url)
        return(r)

    def get_status(self, query_id):
        url = self.base_url + 'filter/%s/status' % query_id
        r = self.get(url)
        return(r)

    def get_exids(self, record_id, sources=None):
        url = self.base_url + 'records/%s/externalreferences' % record_id
        if sources is None:
            r = self.get(url)
        else:
            r = self.get(url, {'dataSources': sources})
        return(r)
