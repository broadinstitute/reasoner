import networkx
import numpy

class Blackboard(networkx.Graph):
    """
    A graph that holds the agent's current knowledge.
    
    The ``Blackboard`` class allows the agent to store, access, and manipulate knowledge.
    It is implemented as a graph (building on top of the networkx package).

    """
    
    def __init__(self):
        super().__init__()
        self.placeholders = list()

    def add_node_from_attributes(self, attributes, entity):
        self.add_node(attributes['name'], entity = entity)
        networkx.set_node_attributes(self, {attributes['name']:attributes})
        return attributes['name']
    
    def add_placeholder(self, entity):
        self.placeholders.append('unknown_' + entity.lower() + '_' + str(len(self.placeholders)))
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
        """Add knowledge to the Blackboard.
        
        Parameters
        ----------
        query : dict
            A dictionary that contains the query nodes, with entity names as keys
            and node names as values.
            
        query : dict
            A dictionary returned as result from an ``Action`` object.
            
        action : Action
            The action used to get ``query_results``.
        
        """
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
  
    def get_path_subgraph(self, sources, targets):
        """Return an induced subgraph of all paths connecting two sets of nodes.
        
        Parameters
        ----------
        sources : list
            A list of node names to be used as path sources.
            
        targets : list
            A list of node names to be used as path targets.
        
        Returns
        -------
        networkx.Graph
            An induced subgraph that contains all nodes and edges between ``sources`` and ``targets``.
        
        """
        bc = networkx.betweenness_centrality_subset(self, sources = sources, targets = targets)
        path_nodes = [key for key,value in bc.items() if value > 0 or key in sources or key in targets]
        return(self.subgraph(path_nodes))

    def prune(self, remove_singletons=True, trim_leaves=False, remove_placeholders=False, sources=None, targets=None):
        """Remove specific parts of the graph.
        
        Parameters
        ----------
        remove_singletons : bool, optional
            Should singletons be removed? [default: True]
            
        trim_leaves : bool, optional
            Iteratively remove all nodes with degree one, effectively
            keeping only nodes that are in cycles? [default: False]
        
        remove_placeholders : bool, optional
            Should placeholder nodes be removed? [default: False]
        
        sources, targets : list, optional
            Lists of node names. If provided, nodes that are not on any path
            between ``sources`` and ``targets`` will be removed. [default: None]
        
        """
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
    
    
  
    def get_entity_nodes(self,entities, include_unbound = False):
        """Get all nodes that are instances of specific entities.
        
        Parameters
        ----------
        entities : list
            A list of entity names.
        
        include_unbound : bool, optional
            Should placeholder nodes be included?
        
        Returns
        -------
        dict
            A dictionary of nodes, indexed by entity names.
        
        """
        node_dict = dict()
        for entity in entities:
            node_dict[entity] = list()
        
        if include_unbound == True:
            for n,d in self.nodes(data=True):
                if d['entity'] in entities:
                    node_dict[d['entity']].append(n)
        else:
            for n,d in self.nodes(data=True):
                if d['entity'] in entities and (not 'unbound' in d or d['unbound'] == False):
                    node_dict[d['entity']].append(n)
        return node_dict
    
    
    def get_entity_edges(self, entity_pairs, include_unbound = False):
        """Get all edges that connect instances of specific entities.
        
        Parameters
        ----------
        entity_pairs : list
            A list of entity name tuples (size 2).
        
        include_unbound : bool, optional
            Should placeholder nodes be included?
        
        Returns
        -------
        dict
            A dictionary of edges, indexed by entity tuples.
        
        """
        edge_dict = dict()
        for entity_pair in entity_pairs:
            edge_dict[entity_pair] = list()
        
        if include_unbound == True:
            for u,v in self.edges():
                etup = (self.nodes[u]['entity'], self.nodes[v]['entity'])
                rev = tuple(reversed(etup))
                if etup in entity_pairs:
                    edge_dict[etup].append((u,v))
                elif rev in entity_pairs:
                    edge_dict[rev].append((v,u))
        else:
            for u,v in self.edges():
                u_bound = (not 'unbound' in self.nodes[u]) or self.nodes[u]['unbound'] == False
                v_bound = (not 'unbound' in self.nodes[v]) or self.nodes[v]['unbound'] == False
                if u_bound and v_bound:
                    etup = (self.nodes[u]['entity'], self.nodes[v]['entity'])
                    rev = tuple(reversed(etup))
                    if etup in entity_pairs:
                        edge_dict[etup].append((u,v))
                    elif rev in entity_pairs:
                        edge_dict[rev].append((v,u))
        return edge_dict

    def write_safe(self):
        """Return a copy of the blackboard graph that is safe to write to GraphML.
        
        Returns
        -------
        graph : ~reasoner.Blackboard.Blackboard
            The write-safe graph.
        
        """
        graph = self.copy()
        for u,v,d in graph.edges(data=True):
            d['entity_source'] = d['entities'][0]
            d['entity_target'] = d['entities'][1]
            del d['entities']
            if 'p' in d and type(d['p']).__module__ == numpy.__name__:
                d['p'] = numpy.asscalar(d['p'])
            if 'cost' in d and type(d['cost']).__module__ == numpy.__name__:
                d['cost'] = numpy.asscalar(d['cost'])
        return graph
    
    
class QueryBuilder():
    """Construct all possible queries from a dictionary of entities (keys) to nodes (values).
    
    Parameters
    ----------
    blackboard : Blackboard
        The blackboard to use for the query.
    
    """
    def __init__(self, blackboard):
        self.query_list = list()
        self.blackboard = blackboard

    def get_all_queries(self, index, n, query):
        #recursively move through the given entities and bind them with all given instances
        if index == n:
            self.query_list.append(query)
        else:
            if isinstance(self.keys[index], tuple):
                for instance in self.instances[self.keys[index]]:
                    q = {**query, **{self.keys[index][0]:instance[0], self.keys[index][1]:instance[1]}}
                    self.get_all_queries(index+1, n, q)
            else:
                for instance in self.instances[self.keys[index]]:
                    q = {**query, **{self.keys[index]:instance}}
                    self.get_all_queries(index+1, n, q)
    
    def get_queries(self, action):
        """Find all possible binding combinations for ``instances``.
        
        Parameters
        ----------
        action : Action
            The action for which to generate queries.
        
        Returns
        -------
        list
            A list queries.
        
        """
        unconnected_entities = list()
        for bound in action.precondition_bindings:
            is_connected = False
            for connection in action.precondition_connections:
                if bound in connection:
                    is_connected = True
                    break
            if is_connected == False:
                unconnected_entities.append(bound)
        
        self.instances = self.blackboard.get_entity_edges(action.precondition_connections)
        self.instances.update(self.blackboard.get_entity_nodes(unconnected_entities))
        
        self.keys = list(self.instances.keys())
        self.get_all_queries(0, len(self.keys), dict())
        return self.query_list