import owlready2
import pandas
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

map_file = "../data/knowledge_graph/id_maps/umls2cellontology.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['cl_id']] = row['umls_id']

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/cl.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


###
ontology_classes = obo.CL_0000000.descendants()
ontology_classes.add(obo.CL_0000000)

kg = KnowledgeGraph()
uq = UmlsQuery()

# add terms
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    if current_id in id_map:
        cui = id_map[current_id]
        umls_result = uq.cui2bestname(cui)
        if umls_result:
            name = umls_result[0]['name']
        else:
            name = current_class.label
    else:
        name = current_class.label
        cui = None
    kg.add_cl_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not isinstance(x, owlready2.entity.Restriction)]
    for superclass in superclasses:
        target_id = superclass.name.replace('_', ':')
        kg.add_isa_relation(current_id, 'ClTerm', 'cl_id', target_id, 'ClTerm', 'cl_id', 'cell_ontology')


### deprecated
# uq = UmlsQuery()
# kg = KnowledgeGraph()

# ## get all targets
# terms = kg.get_cl_terms() ## TODO no cl_ids in knowledge graph yet - either map or load full ontology

# ## loop over targets and get ancestors, then loop until full hierarchy is loaded
# to_process = {obo[cl_id.replace(':', '_')] for cl_id in terms}
# processed = set()

# while to_process:
#     print(len(to_process))
#     current_class = to_process.pop()
#     superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
#     for superclass in superclasses:
#         target_cl_id = superclass.name.replace('_', ':')
#         if target_cl_id in id_map:
#             cui = id_map[target_cl_id]
#             name = uq.cui2bestname(cui)[0]['name']
#         else:
#             cui = None
#             name = superclass.label
#         kg.add_cl_term(current_class.name.replace('_', ':'),
#                     target_cl_id,
#                     name,
#                     cui)
#         if superclass not in processed:
#             to_process.add(superclass)
#     processed.add(current_class)