import owlready2
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

def get_pathways(session):
    result = session.run("MATCH (pathway:Pathway) "
           "WHERE exists(pathway.go_id) "
           "RETURN pathway.go_id as go_id;")
    return(result)

def add_go_term(session, origin_go_id, target_go_id, target_cui, target_name):
    session.run("MATCH (origin:GoTerm {go_id: {origin_go_id}}) "
           "MERGE (target:GoTerm {go_id: {target_go_id}}) "
           "SET target.name = {target_name} "
           "SET target.cui = {target_cui} "
           "MERGE (origin)-[:ISA {source: 'go'}]->(target);",
           origin_go_id=origin_go_id, target_go_id=target_go_id, target_cui=target_cui, target_name=target_name)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/go.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## get all targets
with driver.session() as session:
    pathways = get_pathways(session)

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
                add_go_term(session, current_class.name.replace('_', ':'),
                            target_go_id,
                            umls_results[0]['cui'],
                            umls_results[0]['name'])
                if superclass not in processed:
                    to_process.add(superclass)
        processed.add(current_class)
