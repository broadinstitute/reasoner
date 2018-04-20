import csv
import xml.etree.ElementTree as etree
#from neo4j.v1 import GraphDatabase
#from reasoner.neo4j.Config import Config

# def add_drug(tx, id, name, chembl_id, mechanism):
#     tx.run("MERGE (drug:Drug {id: {id}}) "
#            "SET drug.name = {name} "
#            "SET drug.chembl_id = {chembl_id} "
#            "SET drug.mechanism_of_action = {mechanism}",
#            id=id, name=name, chembl_id=chembl_id, mechanism=mechanism)

# def add_target(tx, id, name, hgnc_id, drug_id):
#     tx.run("MATCH (drug:Drug {id: {drug_id}}) "
#            "MERGE (target:Target {id: {id}}) "
#            "SET target.name = {name} "
#            "SET target.hgnc_id = {hgnc_id} "
#            "MERGE (drug)-[:TARGETS]->(target)",
#            id=id, name=name, drug_id=drug_id, hgnc_id=hgnc_id)

# config = Config().config
# driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


# session.write_transaction(add_drug, drug_id, drug_name, drug_exids['ChEMBL'], drug_mechanism)
# #session.write_transaction(add_target, target_id, target_name, target_synonyms, target_exids, drug_id)
# session.write_transaction(add_target, target_id, target_name, target_exids['HUGO Gene Nomenclature Committee (HGNC)'], drug_id)


dbfile = './data/drugbank.xml'
outfile_drugs = './data/graph/drugs.csv'
outfile_targets = './data/graph/targets.csv'

drug_table = [["id", "name", "chembl_id", "mechanism"]]
target_table = [["id", "name", "hgnc_id", "drug_id"]]

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

    if 'ChEMBL' in drug_exids:
        drug_table.append([drug_id, drug_name, drug_exids['ChEMBL'], drug_mechanism])
    else:
        drug_table.append([drug_id, drug_name, None, drug_mechanism])
    
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

        if 'HUGO Gene Nomenclature Committee (HGNC)' in target_exids:
            target_table.append([target_id, target_name, target_exids['HUGO Gene Nomenclature Committee (HGNC)'], drug_id])
        else:
            target_table.append([target_id, target_name, None, drug_id])


with open(outfile_drugs, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(drug_table)

with open(outfile_targets, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(target_table)

print("done")
