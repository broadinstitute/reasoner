import pandas as pd
from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.SemmedDbTools import SemmedDbTools

sdb_tools = SemmedDbTools()
kg = KnowledgeGraph()

sem2type = {'dsyn': 'Disease',
            'neop': 'Disease',
            'fndg': 'Disease',
            'sosy': 'Symptom',
            'tisu': 'Tissue',
            'bpoc': 'Tissue',
            'blor': 'Tissue',
            'cell': 'Cell',
            'moft': 'Pathway',
            'celf': 'Pathway'}

terms = sdb_tools.get_terms()
for term in terms:
    semtypes = set(term['semtype'].split(','))
    st_raw = semtypes.copy()
    for st in st_raw:
        if st in sem2type:
            semtypes.add(sem2type[term['semtype']])
    kg.add_umls_term("UMLS:" + term['cui'], term['name'], semtypes)

triples = sdb_tools.get_triples()
for triple in triples:
    kg.add_semmed_relation(triple['predicate'],
                           "UMLS:" + triple['subject_cui'],
                           "UMLS:" + triple['object_cui'],
                           triple['count'])
