import csv
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

def query_umls(uq, query_term):
    result = uq.search(query_term)
    if result:
        cui = result['results'][0]['ui']
        name = result['results'][0]['name']

        if cui == 'NONE':
            return {}

        return({'cui': cui, 'name': name})



msigdb_file = './data/c2cp_c5mf_c5bp_v6.1.entrez.gmt'
outfile_pathways = './data/graph/pathways.csv'
outfile_pathway_targets = './data/graph/pathway_targets.csv'
outfile_not_found = './data/pathways_not_found.txt'

pathways = []
with open(msigdb_file) as f:
    for line in f:
        parts = line.strip().split('\t')
        pathways.append({'name':parts[0], 'url':parts[1], 'entrez_ids':parts[2:]})

uq = UmlsQuery()
cuis = [["cui", "umls_name", "msigdb_name"]]
not_found = []
pathway_targets = [["pathway_cui", "target_entrez_id"]]

for pathway in pathways:

    query_base = ' '.join(pathway['name'].split('_')[1:]).lower()
    result = query_umls(uq, query_base + ' pathway')
    if not result:
        result = query_umls(uq, query_base)

    if result:
        cuis.append([result['cui'], result['name'], pathway['name']])
        for target in pathway['entrez_ids']:
            pathway_targets.append([result['cui'], target])
    else:
        not_found.append(pathway['name'])


with open(outfile_pathways, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(cuis)

with open(outfile_pathway_targets, 'w') as f:  
   writer = csv.writer(f)
   writer.writerows(pathway_targets)

with open(outfile_not_found, 'w') as f:
    for item in not_found:
        f.write("%s\n" % item)

print('done')