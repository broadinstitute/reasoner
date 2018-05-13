from reasoner.knowledge_graph.ChemblTools import ChemblTools
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

kg = KnowledgeGraph()
uq = UmlsQuery()
ct = ChemblTools()

chembl_ids = kg.get_chembl_ids()
for chembl_id in chembl_ids:
    print(chembl_id)
    results = ct.get_indication(chembl_id)
    for row in results:
        for disease in uq.mesh2cui(row['mesh_id']):
            kg.add_indication(row['chembl_id'],
                              disease['cui'],
                              disease['name'])
