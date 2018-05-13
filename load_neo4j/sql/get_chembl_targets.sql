SELECT md.chembl_id, md.pref_name as compound_name, standard_value, standard_units, standard_flag,
standard_type, accession, target_type, target_dictionary.pref_name as target_name, component_type
FROM molecule_dictionary md
INNER JOIN activities ON md.molregno = activities.molregno
INNER JOIN assays ON activities.assay_id = assays.assay_id
INNER JOIN target_dictionary ON assays.tid = target_dictionary.tid
INNER JOIN target_components ON assays.tid = target_components.tid
INNER JOIN component_sequences ON target_components.component_id = component_sequences.component_id
WHERE (standard_type = 'Ki' or standard_type = 'IC50')
AND confidence_score = 9
AND standard_relation = '='
AND md.chembl_id = 'CHEMBL1738840';
