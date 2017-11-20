
class Action:
    def __init__(self, precondition, effect):
        self.precondition = precondition
        self.effect = effect
        (self.effect_terms, self.effect_constraints) = self.__parse_effect(effect)
        self.precondition_entities = self.__extract_entities(self.precondition)
        self.effect_entities = self.__extract_entities(self.effect_terms)

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
        for term in term_list:
            if 'connected(' in term:
                entity_set.update(term[10:-1].split(', '))
            elif 'bound(' in term:
                entity_set.add(term[6:-1])
        return(list(entity_set))
    
    def execute(self, input):
        assert len(input) == len(self.precondition_entities)
        pass


