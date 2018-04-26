import owlready2
from neo4j.v1 import GraphDatabase
from reasoner.neo4j.Config import Config
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

def get_diseases(session):
    result = session.run("MATCH (disease:Disease) "
           "WHERE exists(disease.hpo_id) "
           "RETURN disease.hpo_id as hpo_id;")
    return(result)

def add_hpo_term(session, origin_hpo_id, target_hpo_id, target_cui, target_name):
    session.run("MATCH (origin:HpoTerm {hpo_id: {origin_hpo_id}}) "
           "MERGE (target:HpoTerm {hpo_id: {target_hpo_id}}) "
           "SET target.name = {target_name} "
           "SET target.cui = {target_cui} "
           "MERGE (origin)-[:ISA {source: 'hpo'}]->(target);",
           origin_hpo_id=origin_hpo_id, target_hpo_id=target_hpo_id, target_cui=target_cui, target_name=target_name)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/hp.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## get all targets
with driver.session() as session:
    diseases = get_diseases(session)

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['hpo_id'].replace(':', '_')] for record in diseases}
processed = set()

uq = UmlsQuery()
with driver.session() as session:
    while to_process:
        print(len(to_process))
        current_class = to_process.pop()
        superclasses = [x for x in current_class.is_a if not isinstance(x, owlready2.entity.Restriction)]
        for superclass in superclasses:
            target_hpo_id = superclass.name.replace('_', ':')
            umls_results = uq.hpo2cui(target_hpo_id)
            if umls_results:
                add_hpo_term(session, current_class.name.replace('_', ':'),
                            target_hpo_id,
                            umls_results[0]['cui'],
                            umls_results[0]['name'])
                if superclass not in processed:
                    to_process.add(superclass)
        processed.add(current_class)
