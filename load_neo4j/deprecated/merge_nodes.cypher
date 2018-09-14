MATCH (n) WHERE exists(n.cui) AND NOT n.cui = ''
WITH n.cui AS cui, COLLECT(n) AS nodes, COUNT(*) AS count
WHERE count > 1
RETURN [ n in nodes | n.cui] AS cuis, size(nodes) ORDER BY size(nodes) DESC LIMIT 10

MATCH (n) WHERE exists(n.cui) AND NOT n.cui = ''
WITH n.cui AS cui, COLLECT(n) AS nodes, COUNT(*) AS count
WHERE count > 1
CALL apoc.refactor.mergeNodes(nodes) YIELD node
RETURN node