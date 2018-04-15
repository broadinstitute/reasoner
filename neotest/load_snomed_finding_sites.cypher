LOAD CSV WITH HEADERS FROM 'file:///snomed_disease_finding_sites.csv' AS line
MATCH (d:Disease {id: line.disease_cui})
MERGE (t:Tissue {id: line.location_cui})
SET t.name = line.location_str
MERGE (t)-[r:LOCATION_OF]->(d)
SET r.snomed_ct = true;
