import pandas as pd
from reasoner.knowledge_graph.ChemblTools import ChemblTools
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

cop_file = '../data/cop/cop_list_full.csv'
outfile = '../data/knowledge_graph/ready_to_load/diseases.csv'

cop = pd.read_csv(cop_file)
unique_diseases = cop.Condition.unique()

kg = KnowledgeGraph()
uq = UmlsQuery()
ct = ChemblTools()

disease_data = pd.DataFrame(columns=["cui", "name", "hpo_id", "mesh_id"])
for term in unique_diseases:
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
        disease_data = disease_data.append({'cui': 'UMLS:' + cui,
                                            'name': name,
                                            'hpo_id': hpo_id,
                                            'mesh_id': 'MESH:' + mesh_id},
                                           ignore_index=True)


chembl_ids = kg.get_drug_chembl_ids()
for chembl_id in chembl_ids:
    indications = ct.get_indication(chembl_id)
    for row in indications:
        result = uq.mesh2cui(row['mesh_id'])
        if result:
            cui = result[0]['cui']
            mesh_id = result[0]['mesh_id']
            name = uq.cui2bestname(cui)[0]['name']
            hpo_result = uq.cui2hpo(cui)
            if hpo_result:
                hpo_id = hpo_result[0]['hpo_id']
            else:
                hpo_id = ''
            disease_data = disease_data.append({'cui': 'UMLS:' + cui,
                                                'name': name,
                                                'hpo_id': hpo_id,
                                                'mesh_id': 'MESH:' + mesh_id},
                                               ignore_index=True)

disease_data.to_csv(outfile, index=False)
