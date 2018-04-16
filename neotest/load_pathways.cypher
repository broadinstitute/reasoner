LOAD CSV WITH HEADERS FROM 'file:///pathways.csv' AS line
MERGE (pathway:Pathway {id: line.cui})
SET pathway.name = line.umls_name;

LOAD CSV WITH HEADERS FROM 'file:///pathway_targets.csv' AS line
MATCH (pathway:Pathway {id: line.pathway_cui})
MATCH (target:Target {entrez_id: line.target_entrez_id})
MERGE (target)-[:PART_OF]->(pathway);
