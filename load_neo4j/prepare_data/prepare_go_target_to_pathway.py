import pandas
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

go_file = "../data/knowledge_graph/processed/goa_human.csv"
outfile_pathways = "../data/knowledge_graph/ready_to_load/pathways.csv"
outfile_protein2pathways = "../data/knowledge_graph/ready_to_load/protein_to_pathways.csv"

# write protein-pathway connections
go = pandas.read_csv(go_file, low_memory=False)
go = go[['db', 'db_object_id', 'go_id', 'evidence_code', 'aspect']]
go = go[(go['db'] == 'UniProtKB')]
go.to_csv(outfile_pathways, index=False)

# write pathways
uq = UmlsQuery()
unique_goids = go['go_id'].unique()
nids = len(unique_goids)
cui_list = [''] * nids
name_list = [''] * nids
for i, go_id in enumerate(unique_goids):
    print(go_id)
    result = uq.go2cui(go_id)
    if len(result) > 1:
        print(result)
        raise ValueError
    if len(result) == 1:
        cui_list[i] = result[0]['cui']
        name_list[i] = result[0]['name']

go_terms = pandas.DataFrame({'go_id': unique_goids, 'cui': cui_list, 'name': name_list})
go_terms.to_csv(outfile_protein2pathways, index=False)
