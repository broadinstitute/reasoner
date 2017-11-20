from lango.parser import StanfordServerParser
from lango.matcher import match_rules


class QueryParser:
    def __init__(self, port=9501):
        self.parser = StanfordServerParser(port=port)
        self.rules = self.get_rules()
        
    def get_rules(self):
        rules_outcome = {
          '( SBARQ ( WHNP ( WDT ) ( NP:np ) ) ( SQ ( VP ( VBZ:action-o ) ( PP:pp1 ) ( PP:pp2 ) ) ) )': {
            'np': {
                '( NP:relation-o )': {}
            },
            'pp1': {
                '( PP ( TO=to ) ( NP:to_object-o ) )': {},
                '( PP ( IN=from ) ( NP:from_object-o ) )': {}
            },
            'pp2': {
                '( PP ( TO=to ) ( NP:to_object-o ) )': {},
                '( PP ( IN=from ) ( NP:from_object-o ) )': {}
            }
          },

          '( SBARQ ( WHNP ( WDT ) ( NP:np1 ) ) ( SQ ( VP ( VBZ:action-o ) ( NP:np2 ) ( PP:pp ) ) ) )': {
            'np1': {
                '( NP:relation-o )': {}
            },
            'np2': {
                '( NP:from_object-o )': {}
            },
            'pp': {
                '( PP ( TO=to ) ( NP:to_object-o ) )': {}
            }
          },

          '( SBARQ ( WHNP ( WP ) ) ( SQ ( VBZ:action-o ) ( NP ( NP:np ) ( PP:pp ) ) ) )': {
            'np': {
                '( NP:relation-o )': {}
            },
            'pp': {
                '( PP ( IN=between ) ( NP ( NN:from_object-o ) ( CC=and ) ( NN:to_object-o ) ) )': {}
            }
          },

          '( S ( VP ( VB:action-o ) ( NP ( NP:np ) ( PP:pp ) ) ) )': {
            'np': {
                '( NP:relation-o )': {}
            },
            'pp': {
                '( PP ( IN=between ) ( NP ( NN:from_object-o ) ( CC=and ) ( NN:to_object-o ) ) )': {}
            }
          },

          '( NP ( NP ( NN:action-o ) ) ( NP ( NP:np ) ( PP:pp ) ) )': {
            'np': {
                '( NP:relation-o )': {}
            },
            'pp': {
                '( PP ( IN=between ) ( NP ( NN:from_object-o ) ( CC=and ) ( NN:to_object-o ) ) )': {}
            }
          },

          '( SBARQ ( WHNP ( WP ) ) ( SQ ( VBZ:action-o ) ( NP ( NP:np ) ( PP:pp ) ) ) )': {
            'np': {
                '( NP:relation-o )': {}
            },
            'pp': {
                '( PP ( IN=between ) ( NP:compound_object-o ) )': {}
            }
          }
        }


        rules_protects = {
          '( SBARQ ( WHNP ( WDT ) ( NP:np ) ) ( SQ ( VP ( VBP:relation-o ) ( PP:pp ) ) ) )': {
            'np': {
                '( NP:from_object-o )': {}
            },
            'pp': {
                '( PP ( IN=from ) ( NP:to_object-o ) )': {}
            }
          },

          '( FRAG ( SBAR ( WHNP ( WDT ) ) ( S ( NP:np ) ( VP ( VBP:relation-o ) ( PP:pp ) ) ) ) )': {
            'np': {
                '( NP:from_object-o )': {}
            },
            'pp': {
                '( PP ( IN=from ) ( NP:to_object-o ) )': {}
            }
          }
        }

        return({**rules_outcome, **rules_protects})

    def process_matches(self, relation, from_object=None, to_object=None, compound_object=None):
        if compound_object is not None:
            (to_object, from_object) = compound_object.split(' and ')
        return({'from':from_object, 'to':to_object, 'relation':relation})
        
    def parse(self, query):
        tree = self.parser.parse(query)
        return(match_rules(tree, self.rules, self.process_matches))
