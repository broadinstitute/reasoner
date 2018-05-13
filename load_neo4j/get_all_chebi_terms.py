from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

outfile = '../data/neo4j/all_chebi_terms.txt'

kg = KnowledgeGraph()
chebi_terms = [record['chebi_id'] for record in kg.get_chebi_terms()]

with open(outfile,'w') as f:
    for term in chebi_terms:
        f.write("%s\n" % term)
