#!/usr/bin/python

from .Authentication import *
import requests
import json

class UmlsQuery:
    def __init__(self, apikey):
        self.AuthClient = Authentication(apikey)
        self.tgt = self.AuthClient.gettgt()
        
        self.version = 'current'
        self.base_uri = 'https://uts-ws.nlm.nih.gov/rest/'
        

    def get_ticket(self):
        return(self.AuthClient.getst(self.tgt))


    def mesh2cui(self, mesh_id):
        content_endpoint = 'content/' + self.version + '/source/MSH/' + mesh_id + '/atoms/preferred'

        ticket = self.get_ticket()
        query = {'ticket':ticket}
        r = requests.get(self.base_uri+content_endpoint,params=query)
        r.encoding = 'utf-8'

        if not r.ok:
            return({})

        items  = json.loads(r.text)
        jsonData = items['result']

        return({'cui':jsonData['concept'].rsplit('/', 1)[-1], 'name':jsonData['name']})


    def search(self, query_string):
        content_endpoint = "search/" + self.version
        pageNumber=0

        while True:
            ticket = self.get_ticket()
            pageNumber += 1
            query = {'string':query_string,'ticket':ticket, 'pageNumber':pageNumber}
            r = requests.get(self.base_uri+content_endpoint,params=query)
            r.encoding = 'utf-8'

            if not r.ok:
                print(r.url)
                print(r.status_code)
                return({})

            items  = json.loads(r.text)
            jsonData = items["result"]
            
            return(jsonData)

            # print("Results for page " + str(pageNumber)+"\n")
            
            # for result in jsonData["results"]:
                
            #     try:
            #         print("ui: " + result["ui"])
            #     except:
            #         NameError
            #     try:
            #         print("uri: " + result["uri"])
            #     except:
            #         NameError
            #     try:
            #         print("name: " + result["name"])
            #     except:
            #         NameError
            #     try:
            #         print("Source Vocabulary: " + result["rootSource"])
            #     except:
            #         NameError
              
            #     print("\n")
            
            
            # ##Either our search returned nothing, or we're at the end
            # if jsonData["results"][0]["ui"] == "NONE":
            #     break
            # print("*********")

