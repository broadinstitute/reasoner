LOAD CSV WITH HEADERS FROM 'file:///umls2chebi.csv' AS line
MATCH (term:ChebiTerm {chebi_id: line.chebi_id})
WHERE not term:Drug
SET term.cui = replace(line.umls_id, "UMLS:", "");
