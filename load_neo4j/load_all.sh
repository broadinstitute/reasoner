#!/bin/bash

# user=$1
# password=$2

# cypher-shell -u $user -p $password < create_indexes.cypher

# python load_drugs.py
# python load_genes_proteins.py
# python load_drug_target_relations.py
# python load_diseases.py
# python load_indications.py
# python load_semmeddb_data.py
python load_uberon_ontology.py
python load_cell_ontology.py
python load_chebi_ontology.py
python load_gene_ontology.py
python load_disease_finding_sites.py
python load_disease_finding_sites.py
python load_semmed_ontology_connections.py
python load_human_phenotype_ontology.py
python load_symptom_ontology.py
