import pandas as pd
from umls.UmlsQuery import UmlsQuery
from neo4j.v1 import GraphDatabase
from Config import Config


def add_pathway(tx, cui, name, original_name):
    tx.run("MATCH (pathway:Pathway {name: {original_name}}) "
           "MERGE (pathway)-[:HAS_ID]->(:Identifier {id: {cui}, type: 'cui', resource: 'UMLS'}) "
           "MERGE (pathway)-[:HAS_SYNONYM]->(:Synonym {name: {name}, type: 'umls_concept'})",
           cui=cui, name=name, original_name=original_name)


config = Config().config
apikey = Config().config['umls']['apikey']

path_file = './data/c2.cp.v6.1.entrez.gmt'
outfile = './data/cop_pathway_cui.csv'

driver = GraphDatabase.driver(config['neo4j']['host'], auth=(config['neo4j']['user'], config['neo4j']['password']))

uq = UmlsQuery(apikey)
cuis = pd.DataFrame(columns=["cui", "name", "original_name"])
with driver.session() as session:
    with open(path_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            ori_name = parts[0]
            query_term = ' '.join(ori_name.split('_')[1:]).lower() + ' pathway'

            result = uq.search(query_term)
            if result:
                cui = result['results'][0]['ui']
                name = result['results'][0]['name']
                print(name)
                if cui != 'NONE':
                    cuis = cuis.append({'cui': cui,
                                        'name': name,
                                        'original_name': ori_name},
                                       ignore_index=True)
                    session.write_transaction(add_pathway, cui, name, ori_name)

cuis.to_csv(outfile, index=False)
