import pandas as pd
from umls.UmlsQuery import UmlsQuery
from Config import Config

apikey = Config().config['umls']['apikey']

cop_file = './data/cop_benchmark.csv'
outfile = './data/cop_disease_cui.csv'

cop = pd.read_csv(cop_file)

uq = UmlsQuery(apikey)
cuis = pd.DataFrame(columns=["cui", "name", "mesh_id"])
for index, row in cop.iterrows():
    mesh_id = row['Disease_MeSH_ID']
    result = uq.mesh2cui(mesh_id)
    if result:
        result['mesh_id'] = mesh_id
        cuis = cuis.append(result, ignore_index = True)

cuis.to_csv(outfile, index = False)
