import pandas as pd
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

cop_file = '../data/neo4j/cop_list_full.csv'
outfile = '../data/neo4j/graph/diseases.csv'

cop = pd.read_csv(cop_file)
unique_diseases = cop.Condition.unique()

uq = UmlsQuery()

disease_data = pd.DataFrame(columns=["cui", "name", "hpo_id", "mesh_id"])
for term in unique_diseases:
    print(term)
    result = uq.meshterm2cui(term)
    if result:
        cui = result[0]['cui']
        mesh_id = result[0]['mesh_id']
        name = uq.cui2bestname(cui)[0]['name']
        hpo_result = uq.cui2hpo(cui)
        if hpo_result:
            hpo_id = hpo_result[0]['hpo_id']
        else:
            hpo_id = ''
        disease_data = disease_data.append({'cui': cui,
                                            'name': name,
                                            'hpo_id': hpo_id,
                                            'mesh_id': mesh_id},
                                           ignore_index=True)

disease_data.to_csv(outfile, index=False)
