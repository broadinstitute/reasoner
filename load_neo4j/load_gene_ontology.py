import owlready2
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/go.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['go_id'].replace(':', '_')] for record in pathways}
processed = set()

uq = UmlsQuery()
with driver.session() as session:
    while to_process:
        current_class = to_process.pop()
        superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
        for superclass in superclasses:
            target_go_id = superclass.name.replace('_', ':')
            umls_results = uq.go2cui(target_go_id)
            if umls_results:
                kg.add_go_term(session, current_class.name.replace('_', ':'),
                            target_go_id,
                            umls_results[0]['cui'],
                            umls_results[0]['name'])
                if superclass not in processed:
                    to_process.add(superclass)
        processed.add(current_class)
