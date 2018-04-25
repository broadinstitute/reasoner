LOAD CSV WITH HEADERS FROM 'file:///diseases.csv' AS line
MERGE (disease:Disease {cui: line.cui})
SET disease.name =  line.name