LOAD CSV WITH HEADERS FROM 'file:///umls2cellontology.csv' AS line
MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
SET term.cl_id = line.cl_id
SET term:ClTerm;

LOAD CSV WITH HEADERS FROM 'file:///umls2uberon.csv' AS line
MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
SET term.uberon_id = line.uberon_id
SET term:UberonTerm;

LOAD CSV WITH HEADERS FROM 'file:///umls2symptomontology.csv' AS line
MATCH (term {cui: replace(line.umls_id, "UMLS:", "")})
SET term.symp_id = line.symp_id
SET term:SympTerm;
