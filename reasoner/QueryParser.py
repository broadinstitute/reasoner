from lango.parser import StanfordServerParser
from lango.matcher import match_rules
from SPARQLWrapper import SPARQLWrapper, JSON
from .MeshTools import MeshTools


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
            
          '( SBARQ ( WHNP ( WDT ) ( NP:np ) ) ( SQ ( VP ( VBZ:relation-o ) ( PP:pp ) ) ) )': {
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
        return({'from':{'term':from_object}, 'to':{'term':to_object}, 'relation':{'term':relation}})
        
    def parse(self, query):
        tree = self.parser.parse(query)
        terms = match_rules(tree, self.rules, self.process_matches)
        if terms is None:
            return {}
        

        
        mesh = MeshTools()
        terms['from'].update({k:v for k,v in mesh.get_best_term_entity(terms['from']['term']).items() if k in ('entity', 'bound')})
        terms['to'].update({k:v for k,v in mesh.get_best_term_entity(terms['to']['term']).items() if k in ('entity', 'bound')})
        
        if terms['from']['entity'] is None:
            tm = NCITTermMapper()
            terms['from']['entity'] = tm.get_entity(terms['from']['term'])
            terms['from']['bound'] = True
        
        if terms['to']['entity'] is None:
            tm = NCITTermMapper()
            terms['to']['entity'] = tm.get_entity(terms['to']['term'])
            terms['to']['bound'] = True

        if terms['relation']['term'] == 'clinical outcome pathway' and terms['to']['entity'] in ('GeneticCondition', 'Symptom'):
            terms['to']['entity'] = 'Disease'

         ## TESTING ONLY - REMOVE!!!
#        if terms['relation'] == 'clinical outcome pathway':
#            terms['from']['entity'] = 'Drug'
#            terms['from']['bound'] = True
#            terms['to']['entity'] = 'Disease'
#            terms['to']['bound'] = True
#        elif terms['relation'] == 'protects':
#            terms['from']['entity'] = 'GeneticCondition'
#            terms['from']['bound'] = False
#            terms['to']['entity'] = 'Disease'
#            terms['to']['bound'] = True
        return(terms)


class NCITTermMapper():

    def __init__(self):
        super().__init__()
        self.sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql/")
        self.entity_map = {'Disease or Disorder':'Disease', 'Genetic Disorder':'GeneticCondition', 'Pharmacologic Substance':'Drug'}

    def send_query(self, query):
        query = """
                PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
                PREFIX obo-term: <http://purl.obolibrary.org/obo/>
                SELECT DISTINCT ?y ?x ?label
                from <http://purl.obolibrary.org/obo/merged/NCIT>
                WHERE
                {
                VALUES ?x { obo-term:NCIT_C2991 obo-term:NCIT_C1909 obo-term:NCIT_C3101}
                ?y rdfs:subClassOf* ?x.
                ?x rdfs:label ?label.
                ?y oboInOwl:hasExactSynonym ?query.
                FILTER(lcase(str(?query))="%s")
                }
                """ % query.lower()

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return(self.sparql.query().convert())
    
    def get_entity(self, term):
        results = self.send_query(term)
        term_entities = [self.entity_map[result['label']['value']] for result in results["results"]["bindings"]]
        if "Disease" in term_entities and "GeneticCondition" in term_entities:
            term_entities = ["GeneticCondition"]
        if len(term_entities) > 0:
            return(term_entities[0])
        else:
            return(None)
