LOAD CSV WITH HEADERS FROM 'file:///umls2chebi.csv' AS line
MATCH (term:ChebiTerm {chebi_id: line.chebi_id})
WHERE not term:Drug
SET term.cui = replace(line.umls_id, "UMLS:", "");


LOAD CSV WITH HEADERS FROM 'file:///chebi2umls_curated.csv' AS line
MATCH (term:ChebiTerm {chebi_id: line.chebi_id})
SET term.cui = line.cui
SET term.umls_name = line.umls_name;
