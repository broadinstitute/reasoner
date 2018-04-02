LOAD CSV WITH HEADERS FROM 'data/snomed_disease_finding_sites.csv' AS line
MATCH (d:Disease {id: line.disease_cui})
MERGE (t:Tissue {id: line.location_cui, name: line.location_str})-[:LOCATION_OF {source: 'snomed_ct'}]->(d)
MERGE (d)-[:HAS_ID]->(:Identifier {id: line.disease_cui, type: 'cui', resource: 'UMLS'})
MERGE (d)-[:HAS SYNONYM]->(:Synonym {name: line.disease_str, type: 'umls_concept', resource: 'UMLS'})
MERGE (t)-[:HAS_ID]->(:Identifier {id: line.location_cui, type: 'cui', resource: 'UMLS'})
MERGE (t)-[:HAS SYNONYM]->(:Synonym {name: line.location_str, type: 'umls_concept', resource: 'UMLS'})
