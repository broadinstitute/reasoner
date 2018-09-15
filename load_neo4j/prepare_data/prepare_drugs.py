import csv
import pandas
import xml.etree.ElementTree as etree
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery


def xstr(s):
    if s is None:
        return ''
    return str(s)


dbfile = '../data/knowledge_graph/primary/drugbank.xml'
chembl2chebi_file = '../data/knowledge_graph/id_maps/chembl2chebi.tsv'

outfile_drugs = '../data/knowledge_graph/ready_to_load/drugs.csv'
outfile_targets = '../data/knowledge_graph/ready_to_load/targets.csv'
outfile_categories = '../data/knowledge_graph/ready_to_load/drug_categories.csv'


# prepare chebi dict
chembl2chebi_df = pandas.read_csv(chembl2chebi_file,
                                  sep="\t", dtype={'chebi_id': 'str'})
chembl2chebi = {}
for index, row in chembl2chebi_df.iterrows():
    chembl2chebi[row['chembl_id']] = row['chebi_id']


uq = UmlsQuery()

drug_table = [["drugbank_id", "name", "type", "chembl_id", "mechanism", "pharmacodynamics", "chebi_id", "cui", "umls_name"]]
target_table = [["target_drugbank_id", "name", "hgnc_id", "uniprot_id", "drug_drugbank_id"]]
category_table = [["drug_drugbank_id", "category_mesh_id"]]

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

    # get synonyms
    drug_synonyms = []
    for syns in drug.findall('drugbank:synonyms', ns):
        for syn in syns:
            drug_synonyms.append(syn.text)

    # get external ids
    drug_exids = {}
    for exids in drug.findall('drugbank:external-identifiers', ns):
        for exid in exids:
            exid_res = exid.find('drugbank:resource', ns).text
            exid_id = exid.find('drugbank:identifier', ns).text
            drug_exids[exid_res] = exid_id

    # get mechanism and pharmacodynamics
    drug_mechanism = drug.find('drugbank:mechanism-of-action', ns).text
    drug_pharmacodynamics = drug.find('drugbank:pharmacodynamics', ns).text

    # add chembl and chebi ids
    drug_chembl_id = ''
    drug_chebi_id = ''
    if 'ChEMBL' in drug_exids:
        drug_chembl_id = drug_exids['ChEMBL']
        if drug_chembl_id in chembl2chebi:
            drug_chebi_id = 'CHEBI:' + chembl2chebi[drug_chembl_id]

    # get umls cui and name
    drug_cui = ''
    drug_umls_name = ''
    result = uq.drugbank2cui(drug_id)
    if len(result) > 1:
        print(result)
        raise ValueError
    if len(result) == 1:
        drug_cui = result[0]['cui']
        drug_umls_name = result[0]['name']

    if drug_id != '':
        drug_id = 'DRUGBANK:' + drug_id
    if drug_chembl_id != '':
        drug_chembl_id = 'CHEMBL:' + drug_chembl_id
    if drug_cui != '':
        drug_cui = 'UMLS:' + drug_cui

    # add new drug to list
    drug_table.append([xstr(drug_id), xstr(drug_name),
                       xstr(drug_type), xstr(drug_chembl_id),
                       xstr(drug_mechanism), xstr(drug_pharmacodynamics),
                       xstr(drug_chebi_id), xstr(drug_cui), xstr(drug_umls_name)])


    # for category in drug.findall('drugbank:categories/drugbank:category', ns):
    #     mesh_id = category.find('drugbank:mesh-id', ns).text
    #     if mesh_id is not None:
    #         category_table.append([drug_id, mesh_id])


    # for target in drug.findall('drugbank:targets/drugbank:target', ns):
    #     target_id = target.find('drugbank:id', ns).text
    #     target_name = target.find('drugbank:name', ns).text
    
    #     target_synonyms = []
    #     target_exids = {}
    #     for polypeptide in target.findall('drugbank:polypeptide', ns):
    #         for syns in polypeptide.findall('drugbank:synonyms', ns):
    #             for syn in syns:
    #                 target_synonyms.append(syn.text)
            
    #         for exids in polypeptide.findall('drugbank:external-identifiers', ns):
    #             for exid in exids:
    #                 exid_res = exid.find('drugbank:resource', ns).text
    #                 exid_id = exid.find('drugbank:identifier', ns).text
    #                 target_exids[exid_res] = exid_id

    #     hgnc_id = None
    #     uniprot_id = None
    #     if 'HUGO Gene Nomenclature Committee (HGNC)' in target_exids:
    #         hgnc_id = target_exids['HUGO Gene Nomenclature Committee (HGNC)']

    #     if 'UniProtKB' in target_exids:
    #         uniprot_id = target_exids['UniProtKB']

    #     target_table.append([xstr(target_id), xstr(target_name), xstr(hgnc_id), xstr(uniprot_id), xstr(drug_id)])



with open(outfile_drugs, 'w') as f:  
    writer = csv.writer(f)
    writer.writerows(drug_table)

# with open(outfile_targets, 'w') as f:  
#     writer = csv.writer(f)
#     writer.writerows(target_table)

# with open(outfile_categories, 'w') as f:  
#     writer = csv.writer(f)
#     writer.writerows(category_table)

print("done")
