import owlready2
import pandas
from neo4j.v1 import GraphDatabase
from reasoner.knowledge_graph.Config import Config
from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery

def get_symp_terms(session):
    result = session.run("MATCH (term:SympTerm) "
                         "WHERE exists(term.symp_id) "
                         "RETURN term.symp_id as symp_id;")
    return(result)

map_file = "../data/neo4j/graph/umls2symptomontology.csv"
id_map_df = pandas.read_csv(map_file)
id_map = {}
for index, row in id_map_df.iterrows():
    id_map[row['symp_id']] = row['umls_id'].replace("UMLS:", "")

config = Config().config
driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))


## load ontology
owlready2.onto_path.append("/data/owlready")
onto = owlready2.get_ontology("http://purl.obolibrary.org/obo/symp.owl")
onto.load()
obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

## get all targets
with driver.session() as session:
    terms = get_symp_terms(session)

## loop over targets and get ancestors, then loop until full hierarchy is loaded
to_process = {obo[record['symp_id'].replace(':', '_')] for record in terms}
to_process = {x for x in to_process if x is not None}
processed = set()

uq = UmlsQuery()
with driver.session() as session:
    while to_process:
        print(len(to_process))
        current_class = to_process.pop()
        superclasses = [x for x in current_class.is_a
                        if not (isinstance(x, owlready2.entity.Restriction) or
                                isinstance(x, owlready2.class_construct.And))]
        for superclass in superclasses:
            target_symp_id = superclass.name.replace('_', ':')
            if target_symp_id in id_map:
                cui = id_map[target_symp_id]
                umls_result = uq.cui2bestname(cui)
                if umls_result:
                  name = umls_result[0]['name']
                else:
                  name = superclass.label
            else:
                cui = None
                name = superclass.label
            add_symp_term(session, current_class.name.replace('_', ':'),
                        target_symp_id,
                        name,
                        cui)
            if superclass not in processed:
                to_process.add(superclass)
        processed.add(current_class)
