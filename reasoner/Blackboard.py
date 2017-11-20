import networkx

class Blackboard(networkx.Graph):
  def __init__(self):
    super().__init__()
    self.placeholders = list()
  
  def add_connected_node(self, neighbor, node, entity, node_attributes, edge_attributes):
    self.add_node(node, entity = entity)
    networkx.set_node_attributes(self, {node:node_attributes})
    self.add_edge(neighbor, node, entities = (self.nodes[neighbor]['entity'], entity))
    networkx.set_edge_attributes(self, {(neighbor, node):edge_attributes})

  def add_knowledge(self, query_node, query_result):
    for item in query_result:
      for entity,instance_list in item.items():
        for attributes in instance_list:
            self.add_connected_node(query_node, attributes['node']['name'], entity, attributes['node'], attributes['edge'])

  def add_path(self, start, end, query_result, entity_order):
    assert entity_order[0]==self.nodes[start]['entity']
    assert entity_order[-1]==self.nodes[end]['entity']
    
    for path in query_result:
      parents = [start]
      for i in range(1, len(entity_order)-1):
        current_layer = list()       
        if entity_order[i] in path.keys():
          for node_attributes in path[entity_order[i]]:
            self.add_node(node_attributes['name'], entity = entity_order[i])
            networkx.set_node_attributes(self, {node_attributes['name']:node_attributes})
            current_layer.append(node_attributes['name'])
            for parent in parents:
              self.add_edge(parent, node_attributes['name'], entities = (self.nodes[parent]['entity'], entity_order[i]))
        else:
          self.placeholders.append('empty_' + entity_order[i] + '_' + str(len(self.placeholders)))
          self.add_node(self.placeholders[-1], entity=entity_order[i], unbound=True)
          current_layer.append(self.placeholders[-1])
          for parent in parents:
            self.add_edge(parent, self.placeholders[-1], entities = (self.nodes[parent]['entity'], entity_order[i]))
        
        parents = current_layer
            
        if i == (len(entity_order)-2):
          for parent in parents:
            self.add_edge(parent, end, entities = (self.nodes[parent]['entity'], self.nodes[end]['entity']))
  
  def prune(self):
    self.remove_nodes_from(self.placeholders)
    degrees = dict(self.degree())
    while 1 in degrees.values():
      for key,value in degrees.items():
        if(value == 1):
          self.remove_node(key)
      degrees = dict(self.degree())
  
  def get_state(self, graph):
    entities = set(d['entity'] for n,d in graph.nodes(data=True) if not 'unbound' in d)
    bound_nodes = set('bound(' + e + ')' for e in entities)
    connections = set('connected(' + ', '.join(d['entities']) + ')' for u,v,d in graph.edges(data=True))
    return({'state':bound_nodes|connections, 'entities':entities})
    
  def observe_state(self):
    return(self.get_state(self))
  
  def observe_path_state(self, start, end):
    if not networkx.has_path(self, start, end):
        # perform "union" check
        return(self.get_state(self))
    else:
        # check each path individually
        path_states = list()
        for path in networkx.all_shortest_paths(self, source=start, target=end):
            sg = self.subgraph(path)
            path_states.append(self.get_state(sg))
        return(path_states)
            