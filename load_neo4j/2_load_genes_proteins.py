from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph

gene_file = '../data/knowledge_graph/ready_to_load/hgnc_genes_proteins.csv'

kg = KnowledgeGraph()
with open(gene_file) as f:
    first_line = f.readline()
    for line in f:
        items = line.strip(',').split('\t')
        kg.add_gene(hgnc_id=items[0], hgnc_symbol=items[1], entrez_id=items[3], name=items[2])
        kg.add_protein(uniprot_id=items[4], name=items[2])
        kg.add_gene_product_relation(hgnc_id=items[0], uniprot_id=items[4])
