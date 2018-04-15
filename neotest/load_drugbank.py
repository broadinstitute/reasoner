import xml.etree.ElementTree as etree
from neo4j.v1 import GraphDatabase
from Config import Config

def add_drug(tx, id, name, chembl_id, mechanism):
    tx.run("MERGE (drug:Drug {id: {id}}) "
           "SET drug.name = {name} "
           "SET drug.chembl_id = {chembl_id} "
           "SET drug.mechanism_of_action = {mechanism}",
           id=id, name=name, chembl_id=chembl_id, mechanism=mechanism)

def add_target(tx, id, name, hgnc_id, drug_id):
    tx.run("MATCH (drug:Drug {id: {drug_id}}) "
           "MERGE (target:Target {id: {id}}) "
           "SET target.name = {name} "
           "SET target.hgnc_id = {hgnc_id} "
           "MERGE (drug)-[:TARGETS]->(target)",
           id=id, name=name, drug_id=drug_id, hgnc_id=hgnc_id)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

dbfile = './data/drugbank.xml'

tree = etree.parse(dbfile)
root = tree.getroot()

ns = {'drugbank': 'http://www.drugbank.ca'}

with driver.session() as session:
    for drug in root.findall('drugbank:drug', ns):
        drug_name = drug.find('drugbank:name', ns).text
        drug_id = ''
        for did in drug.findall('drugbank:drugbank-id', ns):
            if did.get('primary') is not None:
                drug_id = did.text

        drug_synonyms = []
        for syns in drug.findall('drugbank:synonyms', ns):
            for syn in syns:
                drug_synonyms.append(syn.text)

        drug_exids = {}
        for exids in drug.findall('drugbank:external-identifiers', ns):
            for exid in exids:
                exid_res = exid.find('drugbank:resource', ns).text
                exid_id = exid.find('drugbank:identifier', ns).text
                drug_exids[exid_res] = exid_id

        drug_mechanism = drug.find('drugbank:mechanism-of-action', ns).text
        session.write_transaction(add_drug, drug_id, drug_name, drug_exids['ChEMBL'], drug_mechanism)
        
        for target in drug.findall('drugbank:targets/drugbank:target', ns):
            target_id = target.find('drugbank:id', ns).text
            target_name = target.find('drugbank:name', ns).text
        
            target_synonyms = []
            target_exids = {}
            for polypeptide in target.findall('drugbank:polypeptide', ns):
                for syns in polypeptide.findall('drugbank:synonyms', ns):
                    for syn in syns:
                        target_synonyms.append(syn.text)
                
                for exids in polypeptide.findall('drugbank:external-identifiers', ns):
                    for exid in exids:
                        exid_res = exid.find('drugbank:resource', ns).text
                        exid_id = exid.find('drugbank:identifier', ns).text
                        target_exids[exid_res] = exid_id

            #session.write_transaction(add_target, target_id, target_name, target_synonyms, target_exids, drug_id)
            session.write_transaction(add_target, target_id, target_name, target_exids['HGNC'], drug_id)

print("done")
