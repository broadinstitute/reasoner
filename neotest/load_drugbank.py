import xml.etree.ElementTree as etree
from neo4j.v1 import GraphDatabase
from Config import Config

def add_drug(tx, id, name, synonyms, exids, mechanism):
    tx.run("MERGE (drug:Drug {id: {id}}) "
           "SET drug.name = {name} "
           "SET drug.mechanism_of_action: {mechanism} "
           "MERGE (drug)-[:HAS_SYNONYM]->(:Synonym {name: {name}})",
           id=id, name=name, mechanism=mechanism)

    tx.run("MATCH (drug:Drug {id: $id}) "
           "WITH drug "
           "UNWIND $synonyms as synonym_name "
           "MERGE (synonym:Synonym {name:synonym_name}) "
           "MERGE (drug)-[:HAS_SYNONYM]->(synonym)",
           name=name, id=id, synonyms=synonyms)
    
    for resource,exid in exids.items():
        tx.run("MATCH (drug:Drug {id: $id}) "
               "MERGE (identifier:Identifier {id: $exid, resource: $resource}) "
               "MERGE (drug)-[:HAS_ID]->(identifier)",
            id=id, exid=exid, resource=resource)

def add_target(tx, id, name, synonyms, exids, drug_id):
    tx.run("MATCH (drug:Drug {id: $drug_id}) "
           "MERGE (target:Target {id: $id}) "
           "SET target.name = {name} "
           "MERGE (drug)-[:TARGETS]->(target)",
           id=id, name=name, drug_id=drug_id)

    tx.run("MATCH (target:Target {id: $id}) "
           "WITH target "
           "UNWIND $synonyms as synonym_name "
           "MERGE (synonym:Synonym {name:synonym_name}) "
           "MERGE (target)-[:HAS_SYNONYM]->(synonym)",
           id=id, name=name, synonyms=synonyms)
    
    for resource,exid in exids.items():
        tx.run("MATCH (target:Target {id: $id}) "
               "MERGE (identifier:Identifier {id: $exid, resource: $resource}) "
               "MERGE (target)-[:HAS_ID]->(identifier)",
            id=id, exid=exid, resource=resource)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

dbfile = './data/drugbank.xml'

tree = etree.parse(dbfile)
root = tree.getroot()

ns = {'drugbank': 'http://www.drugbank.ca'}

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

    with driver.session() as session:
        session.write_transaction(add_drug, drug_id, drug_name, drug_synonyms, drug_exids, drug_mechanism)
        for target in drug.findall('drugbank:targets/drugbank:target', ns):
            target_id = target.find('drugbank:id', ns).text
            target_name = target.find('drugbank:name', ns).text
        
        for polypeptide in target.findall('drugbank:polypeptide', ns):
            target_synonyms = []
            for syns in polypeptide.findall('drugbank:synonyms', ns):
                for syn in syns:
                    target_synonyms.append(syn.text)
            target_exids = {}
            for exids in polypeptide.findall('drugbank:external-identifiers', ns):
                for exid in exids:
                    exid_res = exid.find('drugbank:resource', ns).text
                    exid_id = exid.find('drugbank:identifier', ns).text
                    target_exids[exid_res] = exid_id

            session.write_transaction(add_target, target_id, target_name, target_synonyms, target_exids, drug_id)

print("done")





# for drug in root.findall('drugbank:drug', ns):
#     drug_name = drug.find('drugbank:name', ns).text
#     drug_id = ''
#     for did in drug.findall('drugbank:drugbank-id', ns):
#         if did.get('primary') is not None:
#             drug_id = did.text
    
#     drug_synonyms = []
#     for syns in drug.findall('drugbank:synonyms', ns):
#         for syn in syns:
#             drug_synonyms.append(syn.text)
    
#     drug_exids = {}
#     for exids in drug.findall('drugbank:external-identifiers', ns):
#         for exid in exids:
#             exid_res = exid.find('drugbank:resource', ns).text
#             exid_id = exid.find('drugbank:identifier', ns).text
#             drug_exids[exid_res] = exid_id

#     drug_mechanism = drug.find('drugbank:mechanism-of-action', ns).text
#     print(drug_name, drug_id, drug_synonyms, drug_exids, drug_mechanism)



# n = 1
# for drug in root.findall('drugbank:drug', ns):
#     if n > 4: break
#     for target in drug.findall('drugbank:targets/drugbank:target', ns):
#         target_id = target.find('drugbank:id', ns).text
#         target_name = target.find('drugbank:name', ns).text
        
#         for polypeptide in target.findall('drugbank:polypeptide', ns):
#             target_synonyms = []
#             for syns in polypeptide.findall('drugbank:synonyms', ns):
#                 for syn in syns:
#                     target_synonyms.append(syn.text)
#             target_exids = {}
#             for exids in polypeptide.findall('drugbank:external-identifiers', ns):
#                 for exid in exids:
#                     exid_res = exid.find('drugbank:resource', ns).text
#                     exid_id = exid.find('drugbank:identifier', ns).text
#                     target_exids[exid_res] = exid_id
#             print(target_id, target_name, target_synonyms, target_exids)
#     n = n+1




