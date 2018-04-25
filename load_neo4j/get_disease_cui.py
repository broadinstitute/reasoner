import pandas as pd
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

cop_file = './data/cop_list_full.csv'
outfile = './data/graph/diseases.csv'

cop = pd.read_csv(cop_file)
unique_conditions = cop.Condition.unique()

uq = UmlsQuery()
cuis = pd.DataFrame(columns=["cui", "name", "mesh_id", "mesh_term"])
for term in unique_conditions:
    print(term)

    result = uq.search(term, options={'sabs': 'MSH'})
    if result:
        cui = result['results'][0]['ui']
        name = result['results'][0]['name']

        result = uq.get_atoms(cui, options={'sabs': 'MSH'})
        if result:
            mesh_id = result[0]['code'].split('/')[-1]
            mesh_term = result[0]['name']
        else:
            mesh_id = ''
            mesh_term = ''
        cuis = cuis.append({'cui': cui, 'name': name,
                            'mesh_id': mesh_id, 'mesh_term': mesh_term},
                           ignore_index=True)

cuis.to_csv(outfile, index=False)
