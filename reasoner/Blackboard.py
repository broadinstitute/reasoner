import networkx

class Blackboard(networkx.Graph):
  def __init__(self):
    super().__init__()
    self.placeholders = list()

  def add_node_from_attributes(self, attributes, entity):
    self.add_node(attributes['name'], entity = entity)
    networkx.set_node_attributes(self, {attributes['name']:attributes})
    return(attributes['name'])
    
  def add_placeholder(self, entity):
    self.placeholders.append('empty_' + entity + '_' + str(len(self.placeholders)))
    self.add_node(self.placeholders[-1], entity=entity, unbound=True)
    return(self.placeholders[-1])
    
  def add_knowledge(self, query, query_result, action):
    if len(action.effect_entities) == 2:
        for item in query_result:
          for entity,instance_list in item.items():
            for attributes in instance_list:
                n0 = list(query.values())[0]
                n1 = self.add_node_from_attributes(attributes['node'], entity = entity)
                self.add_edge(n0, n1, entities = (next(iter(query)), entity))
                networkx.set_edge_attributes(self, {(n0, n1):attributes['edge']})
    else:
        for path in query_result:
            for edge in action.effect_connections:
                if edge[0] in path:
                    n0 = [self.add_node_from_attributes(attributes['node'], entity = edge[0]) for attributes in path[edge[0]]]
                    if edge[1] in path:
                        n1 = [self.add_node_from_attributes(attributes['node'], entity = edge[1]) for attributes in path[edge[1]]]
                    elif edge[1] in query:
                        n1 = [query[edge[1]]]
                    else:
                        n1 = [self.add_placeholder(edge[1])]
                        path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]
                    
                elif edge[1] in path:
                    n1 = [self.add_node_from_attributes(attributes['node'], entity = edge[1]) for attributes in path[edge[1]]]
                    if edge[0] in path:
                        n0 = [self.add_node_from_attributes(attributes['node'], entity = edge[0]) for attributes in path[edge[0]]]
                    elif edge[0] in query:
                        n0 = [query[edge[0]]]
                    else:
                        n0 = [self.add_placeholder(edge[0])]
                        path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                elif edge[0] in query:
                    n0 = [query[edge[0]]]
                    n1 = [self.add_placeholder(edge[1])]
                    path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]
                elif edge[1] in query:
                    n0 = [self.add_placeholder(edge[0])]
                    path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                    n1 = [query[edge[1]]]
                else:
                    n0 = [self.add_placeholder(edge[0])]
                    n1 = [self.add_placeholder(edge[1])]
                    path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                    path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]
                for start in n0:
                    for end in n1:
                        self.add_edge(start, end, entities = (edge[0], edge[1]))
  
  def prune(self):
    self.remove_nodes_from(self.placeholders)
    degrees = dict(self.degree())
    while 1 in degrees.values():
      for key,value in degrees.items():
        if(value == 1):
          self.remove_node(key)
      degrees = dict(self.degree())
  
  def get_entity_nodes(self,entities):
        node_dict = dict()
        for entity in entities:
            node_dict[entity] = list()
        
        for n,d in self.nodes(data=True):
            if d['entity'] in entities:
                node_dict[d['entity']].append(n)
        return(node_dict)
    
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

    
    
class QueryBuilder():
    
    def __init__(self):
        self.query_list = list()

    def get_all_queries(self, index, n, query):
        if index == n:
            self.query_list.append(query)
        else:
            for instance in self.instances[self.keys[index]]:
                q = {**query, **{self.keys[index]:instance}}
                self.get_all_queries(index+1, n, q)
    
    def get_queries(self, instances):
        self.instances = instances
        self.keys = list(self.instances.keys())
        self.get_all_queries(0, len(self.keys), dict())
        return(self.query_list)