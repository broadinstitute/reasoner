import owlready2
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/go.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


###
ontology_classes = obo.GO_0005575.descendants() # cellular component
ontology_classes |= obo.GO_0003674.descendants() # molecular function
ontology_classes |= obo.GO_0008150.descendants() # biological process
ontology_classes.add(obo.GO_0005575)
ontology_classes.add(obo.GO_0003674)
ontology_classes.add(obo.GO_0008150)

kg = KnowledgeGraph()
uq = UmlsQuery()

# add terms
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    umls_result = uq.go2cui(current_id)
    if umls_result:
        name = umls_result[0]['name']
        cui = 'UMLS:' + umls_result[0]['cui']
    else:
        name = current_class.label
        cui = None
    kg.add_go_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not isinstance(x, owlready2.entity.Restriction)]
    for superclass in superclasses:
        target_id = superclass.name.replace('_', ':')
        kg.add_isa_relation(current_id, 'GoTerm', 'go_id', target_id, 'GoTerm', 'go_id', 'go')





# ## loop over targets and get ancestors, then loop until full hierarchy is loaded
# to_process = {obo[record['go_id'].replace(':', '_')] for record in pathways}
# processed = set()

# kg = KnowledgeGraph()
# uq = UmlsQuery()
# while to_process:
#     current_class = to_process.pop()
#     superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
#     for superclass in superclasses:
#         target_go_id = superclass.name.replace('_', ':')
#         umls_results = uq.go2cui(target_go_id)
#         if umls_results:
#             kg.add_go_term(current_class.name.replace('_', ':'),
#                         target_go_id,
#                         'UMLS:' + umls_results[0]['cui'],
#                         umls_results[0]['name'])
#             if superclass not in processed:
#                 to_process.add(superclass)
#     processed.add(current_class)
