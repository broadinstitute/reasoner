LOAD CSV WITH HEADERS FROM 'file:///diseases.csv' AS line
MERGE (disease:Disease {cui: line.cui})
SET disease.name =  line.name
SET disease.hpo_id =  line.hpo_id
SET disease.mesh_id =  line.mesh_id;
