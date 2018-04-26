import owlready2
from neo4j.v1 import GraphDatabase
from reasoner.neo4j.Config import Config
from reasoner.neo4j.umls.UmlsQuery import UmlsQuery

def get_drugs(session):
    result = session.run("MATCH (drug:Drug) "
           "WHERE exists(drug.chebi_id) "
           "RETURN drug.chebi_id as chebi_id;")
    return(result)

def add_chebi_role(session, origin_chebi_id, target_chebi_id, target_name):
    session.run("MATCH (origin:ChebiTerm {chebi_id: {origin_chebi_id}}) "
           "MERGE (target:ChebiTerm {chebi_id: {target_chebi_id}}) "
           "SET target.name = {target_name} "
           "MERGE (origin)-[:HAS_ROLE {source: 'chebi'}]->(target);",
           origin_chebi_id=origin_chebi_id, target_chebi_id=target_chebi_id, target_name=target_name)

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("file:////home/mwawer/src/reasoner/data/neo4j/chebi.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## get all targets
with driver.session() as session:
    drugs = get_drugs(session)

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['chebi_id'].replace(':', '_')] for record in drugs}
processed = set()

uq = UmlsQuery()
with driver.session() as session:
    while to_process:
        print(len(to_process))
        current_class = to_process.pop()
        restrictions = [x for x in current_class.is_a if isinstance(x, owlready2.entity.Restriction)]
        roles = [r for x in restrictions if isinstance(x.property(), obo.RO_0000087) for r in x.value().is_a]
        for role in roles:
            target_chebi_id = role.name.replace('_', ':')
            add_chebi_role(session, current_class.name.replace('_', ':'), target_chebi_id, role.label)
            if role not in processed:
                to_process.add(role)
        processed.add(current_class)
