from reasoner.knowledge_graph.umls.UmlsQuery import UmlsQuery


uq = UmlsQuery()
#print(uq.get_disease_location('asthma'))

result = uq.search('Rhinitis, Allergic', options={'sabs': 'MSH'})
cui = result['results'][0]['ui']
name = result['results'][0]['name']

result = uq.get_atoms(cui, options={'sabs': 'MSH', 'ttys': 'MH'})
mesh_id = result[0]['code'].split('/')[-1]
mesh_term = result[0]['name']

print(cui, name, mesh_id, mesh_term)
