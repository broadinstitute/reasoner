import owlready2
import pandas
from neo4j.v1 import GraphDatabase
from reasoner.neo4j.Config import Config
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

# def get_uberon_terms(session):
#     result = session.run("MATCH (term:UberonTerm) "
#                          "WHERE exists(term.uberon_id) "
#                          "RETURN term.uberon_id as uberon_id;")
#     return(result)

def add_uberon_term(session, origin_uberon_id, target_uberon_id, target_name, predicate, target_cui=None):
    if target_cui is not None:
        session.run("MATCH (origin:UberonTerm {uberon_id: {origin_uberon_id}}) "
               "MERGE (target:UberonTerm {uberon_id: {target_uberon_id}}) "
               "SET target.name = {target_name} "
               "SET target.cui = {target_cui} "
               "MERGE (origin)-[:%s {source: 'uberon'}]->(target);" % predicate,
               origin_uberon_id=origin_uberon_id, target_uberon_id=target_uberon_id, target_cui=target_cui, target_name=target_name)
    else:
        session.run("MATCH (origin:UberonTerm {uberon_id: {origin_uberon_id}}) "
               "MERGE (target:UberonTerm {uberon_id: {target_uberon_id}}) "
               "SET target.name = {target_name} "
               "MERGE (origin)-[:%s {source: 'uberon'}]->(target);" % predicate,
               origin_uberon_id=origin_uberon_id, target_uberon_id=target_uberon_id, target_name=target_name)

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
    for current_class in ontology_classes:
        superclasses = [x for x in current_class.is_a
                        if not isinstance(x, owlready2.class_construct.And)]
        for superclass in superclasses:
            if isinstance(superclass, owlready2.entity.Restriction) and isinstance(superclass.property(), obo.BFO_0000050):
                target_uberon_id = superclass.value().name.replace('_', ':')
                predicate = 'PART_OF'
            else:
                target_uberon_id = superclass.name.replace('_', ':')
                predicate = 'ISA'

            if target_uberon_id in id_map:
                cui = id_map[target_uberon_id]
                name = uq.cui2bestname(cui)[0]['name']
            else:
                cui = None
                name = superclass.label

            add_uberon_term(session, current_class.name.replace('_', ':'),
                        target_uberon_id,
                        name,
                        predicate,
                        cui)
