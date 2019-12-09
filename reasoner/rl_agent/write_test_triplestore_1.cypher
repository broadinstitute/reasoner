MATCH path = (dr:Drug)-[:HAS_ROLE]->(t:ChebiTerm)--(dis:Disease)--(dr)
UNWIND relationships(path) as r
RETURN startNode(r), r, endNode(r)
