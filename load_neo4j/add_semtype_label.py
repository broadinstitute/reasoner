from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

kg = KnowledgeGraph()
uq = UmlsQuery()

cuis = kg.get_cuis()
for cui in cuis:
    semtypes = uq.get_semtype(cui)
    for record in semtypes:
        kg.set_semtype(cui, record['type_name'].decode())
