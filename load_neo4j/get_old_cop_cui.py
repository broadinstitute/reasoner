import pandas as pd
import json

def get_umls_term(term, ntype):
    result = uq.search(term, options={'sabs': 'MSH'})
    if result and result['results'][0]['ui'] != 'NONE':
        return({'id': result['results'][0]['ui'],
                'name': result['results'][0]['name'],
                'type': ntype})
    else:
        return({'id': 'none', 'name': term, 'type': ntype})

cop_file = './data/cop_overlap.csv'
outfile = './data/cop_overlap_cui.json'

cop = pd.read_csv(cop_file)
cop = cop.loc[cop['origin'] == 'prediction']

uq = UmlsQuery()
paths = []

cols = ['Drug', 'Target', 'Pathway', 'Cell', 'Symptom', 'Disease']

for index, row in cop.iterrows():
    path = {'score': row['probability'], 'nodes': []}
    for col in cols:
        path['nodes'].append(get_umls_term(row[col], col))
    paths.append(path)

with open(outfile, 'w') as f:
    json.dump(paths, f, indent=4)
