import owlready2
import pandas
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

map_file = "../data/knowledge_graph/id_maps/chebi2umls_curated.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['chebi_id']] = 'UMLS:' + row['cui']

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("file:////home/mwawer/src/reasoner/data/neo4j/chebi.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


###
ontology_classes = obo.CHEBI_24431.descendants() # chemical entity
ontology_classes |= obo.CHEBI_50906.descendants() # role
ontology_classes.add(obo.CHEBI_24431)
ontology_classes.add(obo.CHEBI_50906)

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
    kg.add_chebi_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not isinstance(x, owlready2.entity.Restriction)]
    for superclass in superclasses:
        if isinstance(superclass, owlready2.entity.Restriction):
            if isinstance(superclass.property(), obo.RO_0000087):
                target = superclass.value().is_a[0]
                target_id = target.name.replace('_', ':')
                kg.add_has_role_relation(current_id, 'ChebiTerm', 'chebi_id', target_id, 'ChebiTerm', 'chebi_id', 'chebi')
        else:
            target_id = superclass.name.replace('_', ':')
            kg.add_isa_relation(current_id, 'ChebiTerm', 'chebi_id', target_id, 'ChebiTerm', 'chebi_id', 'chebi')


# kg = KnowledgeGraph()
# uq = UmlsQuery()

# ## get all drugs
# drugs = kg.get_drugs()

# ## loop over targets and get ancestors, then loop until full hierarchy is loaded
# to_process = {obo[record['chebi_id'].replace(':', '_')] for record in drugs}

# processed = set()
# while to_process:
#     print(len(to_process))
#     current_class = to_process.pop()
#     restrictions = [x for x in current_class.is_a if isinstance(x, owlready2.entity.Restriction)]
#     roles = [r for x in restrictions if isinstance(x.property(), obo.RO_0000087) for r in x.value().is_a]
#     for role in roles:
#         target_chebi_id = role.name.replace('_', ':')
#         kg.add_chebi_role(current_class.name.replace('_', ':'), target_chebi_id, role.label[0])
#         if role not in processed:
#             to_process.add(role)
#     processed.add(current_class)
