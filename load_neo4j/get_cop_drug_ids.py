import csv
import pandas
from reasoner.neo4j.ChemSpiderTools import ChemSpiderTools

cop_file = '../data/neo4j/cop_benchmark_input_cui_curated.csv'
outfile = '../data/neo4j/cop_chembl_ids.csv'

cop = pandas.read_csv(cop_file)
cst = ChemSpiderTools()

cpd_ids = [['drug_name', 'cui', 'chembl_id', 'chebi_id', 'drugbank_id']]
for index,row in cop.iterrows():
    r = cst.search_name(row['drug_name'])
    if r is None:
        continue
    for record in r['results']:
        exids = cst.get_exids(record, ['ChEMBL', 'ChEBI', 'DrugBank'])
        drug_entry = [row['drug_name'], row['drug_cui'], '', '', '']
        if exids is not None:
            for ref in exids['externalReferences']:
                if ref['source'] == 'ChEMBL':
                    drug_entry[2] = ref['externalId']
                elif ref['source'] == 'ChEBI':
                    drug_entry[3] = ref['externalId']
                elif ref['source'] == 'DrugBank':
                    drug_entry[4] = ref['externalId']
        cpd_ids.append(drug_entry)

with open(outfile, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(cpd_ids)
