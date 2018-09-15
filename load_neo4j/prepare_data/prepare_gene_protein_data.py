import pandas as pd

gene_file = '../data/knowledge_graph/primary/hgnc_genes_proteins.txt'
outfile = '../data/knowledge_graph/ready_to_load/hgnc_genes_proteins.csv'

drugs = pd.read_csv(gene_file, sep='\t', dtype=object)

drugs['entrez_id'] = 'NCBIGENE:' + drugs['entrez_id']
drugs['uniprot_id'] = 'UNIPROT:' + drugs['uniprot_id']

drugs.to_csv(outfile)
