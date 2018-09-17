from reasoner.knowledge_graph.ChemblTools import ChemblTools
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

kg = KnowledgeGraph()
uq = UmlsQuery()
ct = ChemblTools()

chembl_ids = kg.get_drug_chembl_ids()
for chembl_id in chembl_ids:
    indications = ct.get_indication(chembl_id)
    for row in indications:
        result = uq.mesh2cui(row['mesh_id'])
        if result:
            kg.add_indication(row['chembl_id'], result[0]['cui'])
