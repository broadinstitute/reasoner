
class Action:
    def __init__(self, precondition, effect):
        self.precondition = precondition
        self.effect = effect
        (self.effect_terms, self.effect_constraints) = self.__parse_effect(effect)
        (self.precondition_entities, self.precondition_bindings, self.precondition_connections) = self.__extract_entities(self.precondition)
        (self.effect_entities, self.effect_bindings, self.effect_connections) = self.__extract_entities(self.effect_terms) 

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
        connections = list()
        for term in term_list:
            if 'connected(' in term:
                entities = term[10:-1].split(', ')
                entity_set.update(entities)
                connections.append(tuple(entities))
            elif 'bound(' in term:
                entity = term[6:-1]
                entity_set.add(entity)
                entity_bound.add(entity)
        return(list(entity_set), list(entity_bound), connections)
    
    def execute(self, input):
        assert len(input) == len(self.precondition_entities)
        pass


