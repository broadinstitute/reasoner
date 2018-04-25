LOAD CSV WITH HEADERS FROM 'file:///drugs.csv' AS line
MERGE (drug:Drug {drugbank_id: line.id})
SET drug.cui = line.cui
SET drug.name = line.name
SET drug.type = line.type
FOREACH(x IN CASE WHEN line.chembl_id IS NULL THEN [] ELSE [1] END | SET drug.chembl_id = line.chembl_id)
FOREACH(x IN CASE WHEN line.chebi_id IS NULL THEN [] ELSE [1] END | SET drug.chebi_id = line.chebi_id)
FOREACH(x IN CASE WHEN line.mechanism IS NULL THEN [] ELSE [1] END | SET drug.mechanism = line.mechanism)
FOREACH(x IN CASE WHEN line.pharmacodynamics IS NULL THEN [] ELSE [1] END | SET drug.pharmacodynamics = line.pharmacodynamics);


LOAD CSV WITH HEADERS FROM 'file:///targets.csv' AS line
MATCH (drug:Drug {drugbank_id: line.drug_id})
MERGE (target:Target {drugbank_id: line.id})
MERGE (drug)-[:TARGETS]->(target)
SET target.name = line.name
FOREACH(x IN CASE WHEN line.hgnc_id IS NULL THEN [] ELSE [1] END | SET target.hgnc_id = line.hgnc_id)
FOREACH(x IN CASE WHEN line.uniprot_id IS NULL THEN [] ELSE [1] END | SET target.uniprot_id = line.uniprot_id);
