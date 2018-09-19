import owlready2
import pandas
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

map_file = "../data/knowledge_graph/id_maps/umls2uberon.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['uberon_id']] = row['umls_id']

## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/uberon.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")


ontology_classes = obo.UBERON_0001062.descendants()
ontology_classes.add(obo.UBERON_0001062)

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
    kg.add_uberon_term(current_id, name, cui)


# add relations
for current_class in ontology_classes:
    current_id = current_class.name.replace('_', ':')
    superclasses = [x for x in current_class.is_a
                    if not isinstance(x, owlready2.class_construct.And)]
    for superclass in superclasses:
        if isinstance(superclass, owlready2.entity.Restriction):
            if isinstance(superclass.property(), obo.BFO_0000050):
                target = superclass.value().is_a[0]
                target_id = target.name.replace('_', ':')
                kg.add_part_of_relation(current_id, 'UberonTerm', 'uberon_id', target_id, 'UberonTerm', 'uberon_id', 'uberon')
        else:
            target_id = superclass.name.replace('_', ':')
            kg.add_isa_relation(current_id, 'UberonTerm', 'uberon_id', target_id, 'UberonTerm', 'uberon_id', 'uberon')
