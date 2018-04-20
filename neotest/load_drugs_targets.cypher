LOAD CSV WITH HEADERS FROM 'file:///drugs.csv' AS line
MERGE (drug:Drug {id: line.id})
SET drug.name = line.name
FOREACH(x IN CASE WHEN line.chembl_id IS NULL THEN [] ELSE [1] END | SET drug.chembl_id = line.chembl_id)
FOREACH(x IN CASE WHEN line.mechanism IS NULL THEN [] ELSE [1] END | SET drug.mechanism_of_action = line.mechanism);

LOAD CSV WITH HEADERS FROM 'file:///targets.csv' AS line
MATCH (drug:Drug {id: line.drug_id})
MERGE (target:Target {id: line.id})
MERGE (drug)-[:TARGETS]->(target)
SET target.name = line.name
FOREACH(x IN CASE WHEN line.hgnc_id IS NULL THEN [] ELSE [1] END | SET target.hgnc_id = line.hgnc_id);
