import networkx

class Blackboard(networkx.Graph):
    def __init__(self):
        super().__init__()
        self.placeholders = list()

    def add_node_from_attributes(self, attributes, entity):
        self.add_node(attributes['name'], entity = entity)
        networkx.set_node_attributes(self, {attributes['name']:attributes})
        return attributes['name']
    
    def add_placeholder(self, entity):
        self.placeholders.append('empty_' + entity + '_' + str(len(self.placeholders)))
        self.add_node(self.placeholders[-1], entity=entity, unbound=True)
        return self.placeholders[-1]
  
    def align_edge_entities(self, node):
        remove_edges = list()
        for u,v,d in self.edges(node, data=True):
            d['entities'] = (self.nodes[u]['entity'], self.nodes[v]['entity'])
            if u == v:
                remove_edges.append((u,v))
        self.remove_edges_from(remove_edges)
    
    def add_knowledge(self, query, query_result, action):
        if len(action.effect_entities) == 2:
            for item in query_result:
                for entity,instance_list in item.items():
                    for attributes in instance_list:
                        n0 = list(query.values())[0]
                        n1 = self.add_node_from_attributes(attributes['node'], entity = entity)
                        self.add_edge(n0, n1, entities = (next(iter(query)), entity))
                        networkx.set_edge_attributes(self, {(n0, n1):attributes['edge']})
                        self.align_edge_entities(n1)
        elif len(action.effect_entities) == 1:
            for item in query_result:
                for entity,instance_list in item.items():
                    for attributes in instance_list:
                        n0 = self.add_node_from_attributes(attributes['node'], entity = entity)
                        self.align_edge_entities(n0)
        else:
            for path in query_result:
                for edge in action.effect_connections:
                    if edge[0] in path:
                        n0 = {self.add_node_from_attributes(attributes['node'], edge[0]):attributes['edge'] for attributes in path[edge[0]]}
                        if edge[1] in path:
                            n1 = {self.add_node_from_attributes(attributes['node'], edge[1]):attributes['edge'] for attributes in path[edge[1]]}
                        elif edge[1] in query:
                            n1 = {query[edge[1]]:{}}
                        else:
                            n1 = {self.add_placeholder(edge[1]):{}}
                            path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]

                    elif edge[1] in path:
                        n1 = {self.add_node_from_attributes(attributes['node'], edge[1]):attributes['edge'] for attributes in path[edge[1]]}
                        if edge[0] in path:
                            n0 = {self.add_node_from_attributes(attributes['node'], edge[0]):attributes['edge'] for attributes in path[edge[0]]}
                        elif edge[0] in query:
                            n0 = {query[edge[0]]:{}}
                        else:
                            n0 = {self.add_placeholder(edge[0]):{}}
                            path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                    elif edge[0] in query:
                        n0 = {query[edge[0]]:{}}
                        n1 = {self.add_placeholder(edge[1]):{}}
                        path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]
                    elif edge[1] in query:
                        n0 = {self.add_placeholder(edge[0]):{}}
                        path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                        n1 = {query[edge[1]]:{}}
                    else:
                        n0 = {self.add_placeholder(edge[0]):{}}
                        n1 = {self.add_placeholder(edge[1]):{}}
                        path[edge[0]] = [{'node':{'name':node},'edge':{}} for node in n0]
                        path[edge[1]] = [{'node':{'name':node},'edge':{}} for node in n1]

                    edge_attributes = dict()
                    for start,start_eattr in n0.items():
                        for end,end_eattr in n1.items():
                            self.add_edge(start, end, entities = (edge[0], edge[1]))
                            edge_attributes[(start,end)] = end_eattr

                    networkx.set_edge_attributes(self, edge_attributes)
  
    def get_path_subgraph(self):
        bc = networkx.betweenness_centrality_subset(self, sources = sources, targets = targets)
        path_nodes = [key for key,value in bc.items() if value > 0 or key in sources or key in targets]
        return(self.subgraph(path_nodes))

    def prune(self, remove_singletons=True, trim_leaves=False, remove_placeholders=False, sources=None, targets=None):
        if remove_placeholders == True:
            self.remove_nodes_from(self.placeholders)

        if sources is not None and targets is not None:
            bc = networkx.betweenness_centrality_subset(self, sources = sources, targets = targets)
            remove_bc = [key for key,value in bc.items() if value == 0 and not key in sources and not key in targets]
            self.remove_nodes_from(remove_bc)

        if trim_leaves:
            degrees = dict(self.degree())
            while 1 in degrees.values():
                for key,value in degrees.items():
                    if(value == 1):
                        self.remove_node(key)
                degrees = dict(self.degree())

        if remove_singletons:
            degrees = dict(self.degree())
            for key,value in degrees.items():
                if(value == 0):
                    self.remove_node(key)
    
    
  
    def get_entity_nodes(self,entities):
        node_dict = dict()
        for entity in entities:
            node_dict[entity] = list()
        
        for n,d in self.nodes(data=True):
            if d['entity'] in entities:
                node_dict[d['entity']].append(n)
        return node_dict

    
    
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
        return self.query_list