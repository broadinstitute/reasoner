LOAD CSV WITH HEADERS FROM 'file:///diseases.csv' AS line
MERGE (disease:Disease {cui: line.cui})
SET disease.name =  line.name
SET disease.mesh_id =  line.mesh_id
FOREACH(x IN CASE WHEN line.hpo_id IS NULL THEN [] ELSE [1] END | SET disease.hpo_id = line.hpo_id SET disease:HpoTerm);
