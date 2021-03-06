from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

uq = UmlsQuery()
kg = KnowledgeGraph()
result = uq.get_snomed_finding_sites()
for row in result:
    kg.add_disease_finding_site_relation(row['disease_cui'], row['location_cui'])
