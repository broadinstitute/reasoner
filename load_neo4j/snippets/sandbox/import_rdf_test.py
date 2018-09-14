import rdflib
g = rdflib.Graph()
result = g.parse('./data/chembl_23.0_indication.ttl', format='n3')
print(len(g))
for stmt in g:
    print(stmt)