import owlready2
import pandas
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

map_file = "../data/neo4j/graph/umls2symptomontology.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['symp_id']] = row['umls_id']

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/symp.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


###
ontology_classes = obo.SYMP_0000462.descendants()
ontology_classes.add(obo.SYMP_0000462)

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
    kg.add_symp_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not (isinstance(x, owlready2.entity.Restriction) or
                            isinstance(x, owlready2.class_construct.And))]
    for superclass in superclasses:
        target_id = superclass.name.replace('_', ':')
        kg.add_isa_relation(current_id, 'SympTerm', 'symp_id', target_id, 'SympTerm', 'symp_id', 'symp')


# kg = KnowledgeGraph()
# uq = UmlsQuery()
# with driver.session() as session:
#     while to_process:
#         print(len(to_process))
#         current_class = to_process.pop()
#         superclasses = [x for x in current_class.is_a
#                         if not (isinstance(x, owlready2.entity.Restriction) or
#                                 isinstance(x, owlready2.class_construct.And))]
#         for superclass in superclasses:
#             target_symp_id = superclass.name.replace('_', ':')
#             if target_symp_id in id_map:
#                 cui = id_map[target_symp_id]
#                 umls_result = uq.cui2bestname(cui)
#                 if umls_result:
#                   name = umls_result[0]['name']
#                 else:
#                   name = superclass.label
#             else:
#                 cui = None
#                 name = superclass.label
#             add_symp_term(session, current_class.name.replace('_', ':'),
#                         target_symp_id,
#                         name,
#                         cui)
#             if superclass not in processed:
#                 to_process.add(superclass)
#         processed.add(current_class)
