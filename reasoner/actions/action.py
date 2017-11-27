from collections import Counter

class Action:
    """A super class for all actions the agent can use.
    
    Each action needs to specify its preconditions and effects. The precondtions are all state
    variables it needs to be true in order for an action to be executed. The effects are state
    variables that the action can change.
    The main interface to actions is the ``execute`` method.
    
    Parameters
    ----------
    
    precondition : list
       A list of state variable names that need to be true in order for the action to be executable.
       
    effect : list
       A list of state variables that the action will add to the blackboard. Individual values in
       the list are considered to be connected by a logical *or*, meaning that the action may or
       may not change some of them. This is done to allow for uncertainty in the action's effects.
       If two variables always have the same truth value, they should be lsited as one string in the
       list, connected by 'and'.
    
    """
    def __init__(self, precondition, effect):
        self.precondition = precondition
        self.effect = effect
        (self.effect_terms, self.effect_constraints) = self.__parse_effect(effect)
        (self.precondition_entities, self.precondition_bindings, self.precondition_connections) = self.__extract_entities(self.precondition)
        (self.effect_entities, self.effect_bindings, self.effect_connections) = self.__extract_entities(self.effect_terms) 
        ecounter = Counter(x for t in self.effect_connections for x in t)
        self.terminal_effect_entities = [k for k, v in ecounter.items() if v == 1 and not k in self.precondition_entities]
        
    def __parse_effect(self, effect):
        parsed_effect = list()
        parsed_constraints = list()
        for term in effect:
          if ' and ' in term:
            term_list = term.split(' and ')
            parsed_constraints.append(tuple(term_list))
            parsed_effect.extend(term_list)
          else:
            parsed_effect.append(term)
        return((parsed_effect, parsed_constraints))
    
    def __extract_entities(self, term_list):
        entity_set = set()
        entity_bound = set()
        connections = set()
        for term in term_list:
            if 'connected(' in term:
                entities = [x.strip() for x in term[10:-1].split(',')]
                entity_set.update(entities)
                connections.add(tuple(entities))
            elif 'bound(' in term:
                entity = term[6:-1]
                entity_set.add(entity)
                entity_bound.add(entity)
        return(list(entity_set), list(entity_bound), list(connections))
    
    def execute(self, input):
        """Execute an action.
        
        Parameters
        ----------
        input : dict
            A dictionary of specific instances, indexed by their entity.
        
        Returns
        -------
        list
            A list of query results. Each entry is a dictionary that indexes lists of nodes by entities.
        
        """
        assert len(input) == len(self.precondition_entities)
        pass


