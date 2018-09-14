from reasoner.knowledge_graph.KnowledgeGraph import KnowledgeGraph
from reasoner.knowledge_graph.ChemblTools import ChemblTools

kg = KnowledgeGraph()
chembl = ChemblTools()

drugs = kg.get_drug_chembl_ids()
for chembl_id in drugs:
    targets = chembl.get_targets(chembl_id)
    for target in targets:
        if target['component_type'] == 'PROTEIN' and target['db_source'] == 'SWISS-PROT':
            kg.add_drug_target_relation(
                drug_chembl_id=target['chembl_id'],
                target_type='Protein',
                target_id_type='uniprot_id',
                target_id='UNIPROT:' + target['accession'],
                activity_value=target['standard_value'],
                activity_type=target['standard_type'],
                activity_unit=target['standard_units'])
