import csv
import xml.etree.ElementTree as etree

dbfile = '../data/neo4j/drugbank.xml'
outfile_drugs = '../data/neo4j/graph/drugs.csv'
outfile_targets = '../data/neo4j/graph/targets.csv'
outfile_categories = '../data/neo4j/graph/drug_categories.csv'

drug_table = [["id", "name", "type", "chembl_id", "mechanism", "pharmacodynamics"]]
target_table = [["id", "name", "hgnc_id", "uniprot_id", "drug_id"]]
category_table = [["drug_id", "mesh_id"]]

tree = etree.parse(dbfile)
root = tree.getroot()

ns = {'drugbank': 'http://www.drugbank.ca'}

for drug in root.findall('drugbank:drug', ns):
    drug_name = drug.find('drugbank:name', ns).text
    drug_type = drug.get('type')
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
    drug_pharmacodynamics = drug.find('drugbank:pharmacodynamics', ns).text

    if 'ChEMBL' in drug_exids:
        drug_table.append([drug_id, drug_name, drug_type, drug_exids['ChEMBL'], drug_mechanism, drug_pharmacodynamics])
    else:
        drug_table.append([drug_id, drug_name, None, drug_mechanism])


    for category in drug.findall('drugbank:categories/drugbank:category', ns):
        mesh_id = category.find('drugbank:mesh-id', ns).text
        if mesh_id is not None:
            category_table.append([drug_id, mesh_id])


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

        hgnc_id = None
        uniprot_id = None
        if 'HUGO Gene Nomenclature Committee (HGNC)' in target_exids:
            hgnc_id = target_exids['HUGO Gene Nomenclature Committee (HGNC)']

        if 'UniProtKB' in target_exids:
            uniprot_id = target_exids['UniProtKB']

        target_table.append([target_id, target_name, hgnc_id, uniprot_id, drug_id])



with open(outfile_drugs, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(drug_table)

with open(outfile_targets, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(target_table)

with open(outfile_categories, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(category_table)

print("done")
