import pandas as pd
from umls.UmlsQuery import UmlsQuery
from neo4j.v1 import GraphDatabase
from Config import Config

def add_pathway(tx, cui, umls_name, msigdb_name, url, entrez_ids):
    tx.run("MERGE (pathway:Pathway {id: {cui}}) "
           "SET pathway.name = {umls_name} "
           "SET pathway.url = {url} "
           "MERGE (pathway)-[:HAS_ID]->(:Identifier {id: {cui}, type: 'cui', resource: 'UMLS'}) "
           "MERGE (pathway)-[:HAS_SYNONYM]->(:Synonym {name: {umls_name}, type: 'umls_concept', resource: 'UMLS'}) "
           "MERGE (pathway)-[:HAS_SYNONYM]->(:Synonym {name: {msigdb_name}, type: 'msigdb_pathway', resource: 'MSigDB'}) "
           "WITH pathway "
           "UNWIND {entrez_ids} as entrez_id "
           "MATCH (item:Target)-[:HAS_ID]->(identifier:Identifier {id: entrez_id, type: 'entrez_gene_id'}) "
           "MERGE (item)-[:PART_OF]->(pathway)",
        cui=cui, umls_name=umls_name, msigdb_name=msigdb_name, url=url, entrez_ids=entrez_ids)


def add_pathway_noumls(tx, msigdb_name, url, entrez_ids):
    tx.run("MERGE (pathway:Pathway {name: {msigdb_name}}) "
           "SET pathway.url = {url} "
           "MERGE (pathway)-[:HAS_SYNONYM]->(:Synonym {name: {msigdb_name}, type: 'msigdb_pathway', resource: 'MSigDB'}) "
           "WITH pathway "
           "UNWIND {entrez_ids} as entrez_id "
           "MATCH (item:Target)-[:HAS_ID]->(identifier:Identifier {id: entrez_id, type: 'entrez_gene_id'}) "
           "MERGE (item)-[:PART_OF]->(pathway)",
        msigdb_name=msigdb_name, url=url, entrez_ids=entrez_ids)


def get_pathway_names(session):
    result = session.run("MATCH (p:Pathway)-[:HAS_SYNONYM]->(s:Synonym {type: 'msigdb_pathway'}) RETURN s.name as msigdb_name")
    return([record['msigdb_name'] for record in result])


def query_umls(uq, query_term):
    result = uq.search(query_term)
    if result:
        cui = result['results'][0]['ui']
        name = result['results'][0]['name']

        if cui == 'NONE':
            return {}

        return({'cui': cui, 'name': name})


config = Config().config
apikey = config['umls']['apikey']
driver = GraphDatabase.driver(
    config['neo4j']['host'],
    auth=(config['neo4j']['user'], config['neo4j']['password']))

msigdb_file = './data/c2cp_c5mf_c5bp_v6.1.entrez.gmt'
outfile = './data/cop_pathway_cui.csv'

pathways = []
with open(msigdb_file) as f:
    for line in f:
        parts = line.strip().split('\t')
        pathways.append({'name':parts[0], 'url':parts[1], 'entrez_ids':parts[2:]})

uq = UmlsQuery(apikey)
cuis = pd.DataFrame(columns=["cui", "umls_name", "msigdb_name"])
with driver.session() as session:
    existing_pathways = get_pathway_names(session)
    for pathway in pathways:
        
        if pathway['name'] in existing_pathways:
            continue

        query_base = ' '.join(pathway['name'].split('_')[1:]).lower()
        result = query_umls(uq, query_base + ' pathway')
        if not result:
            result = query_umls(uq, query_base)

        if result:
            cuis = cuis.append({'cui':result['cui'], 'umls_name':result['name'], 'msigdb_name':pathway['name']}, ignore_index=True)
            session.write_transaction(add_pathway, result['cui'], result['name'], pathway['name'], pathway['url'], pathway['entrez_ids'])
        else:
            cuis = cuis.append({'cui':'na', 'umls_name':'na', 'msigdb_name':pathway['name']}, ignore_index=True)
            session.write_transaction(
                add_pathway_noumls,
                pathway['name'], pathway['url'], pathway['entrez_ids'])

cuis.to_csv(outfile, index=False)
print('done')