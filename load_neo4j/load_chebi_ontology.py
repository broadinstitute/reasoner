import owlready2
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("file:////home/mwawer/src/reasoner/data/neo4j/chebi.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


kg. = KnowledgeGraph()
uq = UmlsQuery()

## get all drugs
drugs = kg.get_drugs()

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['chebi_id'].replace(':', '_')] for record in drugs}

processed = set()
while to_process:
    print(len(to_process))
    current_class = to_process.pop()
    restrictions = [x for x in current_class.is_a if isinstance(x, owlready2.entity.Restriction)]
    roles = [r for x in restrictions if isinstance(x.property(), obo.RO_0000087) for r in x.value().is_a]
    for role in roles:
        target_chebi_id = role.name.replace('_', ':')
        kg.add_chebi_role(current_class.name.replace('_', ':'), target_chebi_id, role.label[0])
        if role not in processed:
            to_process.add(role)
    processed.add(current_class)
