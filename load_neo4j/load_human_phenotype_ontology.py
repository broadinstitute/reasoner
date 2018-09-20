import owlready2
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/hp.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

###
trials = 0
while trials < 10:
    try:
        ontology_classes = obo.HP_0000001.descendants()
    except ValueError:
        trials = trials + 1
        continue

# ontology_classes = obo.HP_0031797.descendants()
# ontology_classes = obo.HP_0012823.descendants()
# ontology_classes = obo.HP_0040279.descendants()
# ontology_classes = obo.HP_0000005.descendants()
# ontology_classes = obo.UPHENO_0001001.descendants()
# ontology_classes.add(obo.HP_0000001)
# ontology_classes.add(obo.HP_0031797)
# ontology_classes.add(obo.HP_0012823)
# ontology_classes.add(obo.HP_0040279)
# ontology_classes.add(obo.HP_0000005)
# ontology_classes.add(obo.UPHENO_0001001)


kg = KnowledgeGraph()
uq = UmlsQuery()

# add terms
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    umls_result = uq.hpo2cui(current_id)
    if umls_result:
        name = umls_result[0]['name']
        cui = 'UMLS:' + umls_result[0]['cui']
    else:
        name = current_class.label
        cui = None
    kg.add_hpo_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not isinstance(x, owlready2.entity.Restriction)]
    for superclass in superclasses:
        target_id = superclass.name.replace('_', ':')
        kg.add_isa_relation(current_id, 'HpoTerm', 'hpo_id', target_id, 'HpoTerm', 'hpo_id', 'hpo')



# ## get all targets
# with driver.session() as session:
#     diseases = get_diseases(session)

# ## loop over targets and get ancestors, then loop until full hierarchy is loaded
# to_process = {obo[record['hpo_id'].replace(':', '_')] for record in diseases}
# processed = set()

# kg = KnowledgeGraph()
# uq = UmlsQuery()
# with driver.session() as session:
#     while to_process:
#         print(len(to_process))
#         current_class = to_process.pop()
#         superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
#         for superclass in superclasses:
#             target_hpo_id = superclass.name.replace('_', ':')
#             umls_results = uq.hpo2cui(target_hpo_id)
#             if umls_results:
#                 add_hpo_term(session, current_class.name.replace('_', ':'),
#                             target_hpo_id,
#                             umls_results[0]['cui'],
#                             umls_results[0]['name'])
#                 if superclass not in processed:
#                     to_process.add(superclass)
#         processed.add(current_class)
