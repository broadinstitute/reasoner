import owlready2
import pandas
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

# def get_uberon_terms(session):
#     result = session.run("MATCH (term:UberonTerm) "
#                          "WHERE exists(term.uberon_id) "
#                          "RETURN term.uberon_id as uberon_id;")
#     return(result)

def add_term(session, term_id, term_name, term_cui=None):
    base_query = ("MERGE (term:UberonTerm {uberon_id: {term_id}}) "
                  "SET term.name = {term_name}")
    if term_cui is not None:
        query = base_query + " SET term.cui = {term_cui};"
    else:
        query = base_query + ";"
    session.run(query, term_id=term_id, term_name=term_name, term_cui=term_cui)


def add_relation(session, origin_id, target_id, predicate):
    session.run("MATCH (origin:UberonTerm {uberon_id: {origin_id}}) "
                "MATCH (target:UberonTerm {uberon_id: {target_id}}) "
                "MERGE (origin)-[:%s {source: 'uberon'}]->(target);" % predicate,
                origin_id=origin_id, target_id=target_id)


map_file = "../data/neo4j/graph/umls2uberon.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['uberon_id']] = row['umls_id'].replace("UMLS:", "")

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/uberon.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

# ## get all targets
# with driver.session() as session:
#     terms = get_uberon_terms(session)

# ## loop over targets and get ancestors, then loop until full hierarchy is loaded
# to_process = {obo[record['uberon_id'].replace(':', '_')] for record in terms}
# to_process = {x for x in to_process if x is not None}
# processed = set()

ontology_classes = obo.UBERON_0001062.descendants()
ontology_classes.add(obo.UBERON_0001062)

uq = UmlsQuery()
with driver.session() as session:
    # add terms
    for current_class in ontology_classes:
        current_id = current_class.name.replace('_', ':')
        if current_id in id_map:
            print(current_id)
            cui = id_map[current_id]
            umls_result = uq.cui2bestname(cui)
            if umls_result:
                name = umls_result[0]['name']
            else:
                name = current_class.label
        else:
            cui = None
            name = current_class.label
        add_term(session, current_id, name, cui)
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
                    predicate = 'PART_OF'
                    print(target_id, 'part of')
                    add_relation(session, current_id, target_id, predicate)
            else:
                target_id = superclass.name.replace('_', ':')
                predicate = 'ISA'
                print(target_id, 'is a')
                add_relation(session, current_id, target_id, predicate)
