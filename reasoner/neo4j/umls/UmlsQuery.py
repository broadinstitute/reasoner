#!/usr/bin/python

import requests
import json
import mysql.connector
from .Authentication import *
from ..Config import Config


class UmlsQuery:
    def __init__(self):
        config = Config().config
        self.AuthClient = Authentication(Config().config['umls']['apikey'])
        self.tgt = self.AuthClient.gettgt()
        self.version = 'current'
        self.base_uri = 'https://uts-ws.nlm.nih.gov/rest/'

        # Open database connection
        self.db = mysql.connector.connect(user=config['umls-db']['user'], password=config['umls-db']['password'],
                              host=config['umls-db']['host'],
                              database=config['umls-db']['database'])

    def db_select(self, sql):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except:
            print("Error: unable to fetch data")
        return(results)

    def get_ticket(self):
        return(self.AuthClient.getst(self.tgt))

    def send_query(self, endpoint, options={}):
        if endpoint.startswith('https://'):
            url = endpoint
        else:
            url = self.base_uri + endpoint

        pageNumber = 0
        while True:
            ticket = self.get_ticket()
            pageNumber += 1
            query = {'ticket': ticket, 'pageNumber': pageNumber}
            query.update(options)
            r = requests.get(url, params=query)
            r.encoding = 'utf-8'

            if not r.ok:
                print(r.url)
                print(r.status_code)
                return({})
            items = json.loads(r.text)
            jsonData = items["result"]
            return(jsonData)

    def get_atoms(self, cui, options={}):
        endpoint = ('content/' + self.version + '/CUI/' + cui + '/atoms')
        return(self.send_query(endpoint, options))

    def mesh2cui(self, mesh_id):
        # content_endpoint = ('content/' + self.version + '/source/MSH/' +
        #                     mesh_id + '/atoms/preferred')
        # ticket = self.get_ticket()
        # query = {'ticket': ticket}
        # r = requests.get(self.base_uri + content_endpoint, params=query)
        # r.encoding = 'utf-8'

        # if not r.ok:
        #     return({})
        # items = json.loads(r.text)
        # jsonData = items['result']

        # return({'cui': jsonData['concept'].rsplit('/', 1)[-1],
        #         'name': jsonData['name']})
        sql = ("SELECT DISTINCT cui, str as name "
               "FROM MRCONSO "
               "WHERE cui IN (SELECT DISTINCT cui FROM MRCONSO WHERE SDUI = '%s' AND SAB = 'MSH') "
               "AND ts = 'P' "
               "AND stt = 'PF' "
               "AND ispref = 'Y' "
               "AND lat = 'ENG';"  % mesh_id)
        result = self.db_select(sql)
        return(result)


    def go2cui(self, go_id):
        sql = ("SELECT DISTINCT cui, str as name "
               "FROM MRCONSO "
               "WHERE cui IN (SELECT DISTINCT cui FROM MRCONSO WHERE SDUI = '%s' AND SAB = 'GO') "
               "AND ts = 'P' "
               "AND stt = 'PF' "
               "AND ispref = 'Y' "
               "AND lat = 'ENG';"  % go_id)
        result = self.db_select(sql)
        return(result)

    def search(self, query_string, options={}):
        endpoint = "search/" + self.version
        query = {'string': query_string}
        query.update(options)
        return(self.send_query(endpoint, query))

    def get_snomed_finding_site(self, snomed_id):
        endpoint = ('content/' + self.version +
                    '/source/SNOMEDCT_US/' + snomed_id + '/relations')
        query = {'includeAdditionalRelationLabels': 'has_finding_site'}
        return(self.send_query(endpoint, query))

    def get_disease_location(self, disease_term):
        result = self.search(disease_term,
                             options={'sabs': 'SNOMEDCT_US',
                                      'returnIdType': 'sourceUi'})
        snomed_id = result['results'][0]['ui']
        result = self.get_snomed_finding_site(snomed_id)
        snomed_relation_url = result[0]['relatedId']
        ui = snomed_relation_url.split('/')[-1]
        result = self.search(ui, {'inputType': 'sourceUi',
                             'searchType': 'exact', 'sabs': 'SNOMEDCT_US'})
        return({'cui': result['results'][0]['ui'], 'name': result['results'][0]['name']})

    def __del__(self):
        self.db.close()
