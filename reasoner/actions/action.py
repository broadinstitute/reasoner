from collections import Counter

class Action:
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
        assert len(input) == len(self.precondition_entities)
        pass


