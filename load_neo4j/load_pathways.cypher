LOAD CSV WITH HEADERS FROM 'file:///pathways.csv' AS line
MATCH (target:Target {uniprot_id: line.db_object_id})
MERGE (pathway:Pathway {go_id: line.go_id})
SET pathway:GoTerm
SET pathway.name = line.name
SET pathway.type = line.aspect
FOREACH(x IN CASE WHEN line.cui IS NULL THEN [] ELSE [1] END | SET pathway.cui = line.cui)
MERGE (target)-[r:PART_OF]->(pathway)
SET r.evidence = line.evidence_code;
