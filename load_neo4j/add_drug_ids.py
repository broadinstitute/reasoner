import pandas
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

drugs_file = '../data/neo4j/drugbank_drugs.csv'
chembl2chebi_file = '../data/neo4j/chembl2chebi.tsv'
outfile = '../data/neo4j/graph/drugs.csv'


drugs = pandas.read_csv(drugs_file)
chembl2chebi = pandas.read_csv(chembl2chebi_file,
                               sep="\t", dtype={'chebi_id': 'int'})

drugs = drugs.join(chembl2chebi.set_index('chembl_id'),
                   on='chembl_id')


uq = UmlsQuery()

unique_dbids = drugs['id'].unique()
nids = len(unique_dbids)
cui_list = ['']*nids
name_list = ['']*nids
for i, db_id in enumerate(unique_dbids):
    print(db_id)
    result = uq.drugbank2cui(db_id)
    if len(result) > 1:
        print(result)
        raise ValueError
    if len(result) == 1:
        cui_list[i] = result[0]['cui']
        name_list[i] = result[0]['name']

drugbank2cui = pandas.DataFrame({'id': unique_dbids,
                                 'cui': cui_list,
                                 'name': name_list})

drugs = drugs.drop(columns=['name'])
drugs = drugs.join(drugbank2cui.set_index('id'), on='id')

drugs.to_csv(outfile, index=False)
