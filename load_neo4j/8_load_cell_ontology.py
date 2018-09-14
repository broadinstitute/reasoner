import owlready2
import pandas
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

def get_cl_terms(session):
    result = session.run("MATCH (term:ClTerm) "
           "WHERE exists(term.cl_id) "
           "RETURN term.cl_id as cl_id;")
    return(result)

def add_cl_term(session, origin_cl_id, target_cl_id, target_name, target_cui=None):
    if target_cui is not None:
        session.run("MATCH (origin:ClTerm {cl_id: {origin_cl_id}}) "
               "MERGE (target:ClTerm {cl_id: {target_cl_id}}) "
               "SET target.name = {target_name} "
               "SET target.cui = {target_cui} "
               "MERGE (origin)-[:ISA {source: 'cl'}]->(target);",
               origin_cl_id=origin_cl_id, target_cl_id=target_cl_id, target_cui=target_cui, target_name=target_name)
    else:
        session.run("MATCH (origin:ClTerm {cl_id: {origin_cl_id}}) "
               "MERGE (target:ClTerm {cl_id: {target_cl_id}}) "
               "SET target.name = {target_name} "
               "MERGE (origin)-[:ISA {source: 'cl'}]->(target);",
               origin_cl_id=origin_cl_id, target_cl_id=target_cl_id, target_name=target_name)

map_file = "../data/neo4j/graph/umls2cellontology.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
  id_map[row['cl_id']] = row['umls_id'].replace("UMLS:", "")

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/cl.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## get all targets
with driver.session() as session:
    terms = get_cl_terms(session)

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['cl_id'].replace(':', '_')] for record in terms}
processed = set()

uq = UmlsQuery()
with driver.session() as session:
    while to_process:
        print(len(to_process))
        current_class = to_process.pop()
        superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
        for superclass in superclasses:
            target_cl_id = superclass.name.replace('_', ':')
            if target_cl_id in id_map:
                cui = id_map[target_cl_id]
                name = uq.cui2bestname(cui)[0]['name']
            else:
                cui = None
                name = superclass.label
            add_cl_term(session, current_class.name.replace('_', ':'),
                        target_cl_id,
                        name,
                        cui)
            if superclass not in processed:
                to_process.add(superclass)
        processed.add(current_class)
