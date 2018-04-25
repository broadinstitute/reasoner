import pandas
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

go_file = "../data/neo4j/goa_human.csv"
outfile = "../data/neo4j/graph/go_pathways.csv"

go = pandas.read_csv(go_file, low_memory = False)

go = go[['db', 'db_object_id', 'go_id', 'evidence_code', 'aspect']]
go = go[(go['db'] == 'UniProtKB') & ((go['aspect'] == 'P') | (go['aspect'] == 'F'))]


uq = UmlsQuery()

unique_goids = go['go_id'].unique()
nids = len(unique_goids)
cui_list = ['']*nids
name_list = ['']*nids
for i, go_id in enumerate(unique_goids):
    print(go_id)
    result = uq.go2cui(go_id)
    if len(result) > 1:
        print(result)
        raise ValueError
    if len(result) == 1:
        cui_list[i] = result[0]['cui']
        name_list[i] = result[0]['name']

go2cui = pandas.DataFrame({'go_id': unique_goids, 'cui': cui_list, 'name': name_list})

go = go.join(go2cui.set_index('go_id'), on = 'go_id')

go.to_csv(outfile, index = False)
