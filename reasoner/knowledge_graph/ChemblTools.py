import mysql.connector
from .Config import Config
from .Dbtools import db_select


class ChemblTools:
    def __init__(self):
        config = Config().config
        self.db = mysql.connector.connect(user=config['chembl']['user'],
                                          password=config['chembl']['password'],
                                          host=config['chembl']['host'],
                                          database=config['chembl']['database'])

    def __del__(self):
        self.db.close()

    def get_indication(self, chembl_id):
        sql = ("SELECT di.*, md.chembl_id "
               "FROM drug_indication AS di "
               "JOIN molecule_dictionary AS md "
               "ON md.molregno = di.molregno "
               "WHERE chembl_id = %s")
        return(db_select(self.db, sql))

    def get_targets(self, chembl_id):
        sql = ("SELECT DISTINCT md.chembl_id as chembl_id, cs.component_id as component_id, "
               "standard_value, standard_units, standard_flag, standard_type, "
               "accession, target_type, td.pref_name as target_name, component_type, db_source, MAX(CONCAT(standard_type, docs.year)) as typeyear "
               "FROM molecule_dictionary md "
               "INNER JOIN activities ON md.molregno = activities.molregno "
               "INNER JOIN assays ON activities.assay_id = assays.assay_id "
               "INNER JOIN target_dictionary td ON assays.tid = td.tid "
               "INNER JOIN target_components tc ON assays.tid = tc.tid "
               "INNER JOIN component_sequences cs ON tc.component_id = cs.component_id "
               "INNER JOIN docs on assays.doc_id = docs.doc_id "
               "WHERE (standard_type = 'Ki' or standard_type = 'IC50') "
               "AND confidence_score = 9 "
               "AND standard_relation = '=' "
               "AND cs.tax_id = 9606 "
               "AND md.chembl_id = '%s' "
               "GROUP BY accession;") % chembl_id
        return(db_select(self.db, sql))

# "ORDER BY accession, standard_type DESC, docs.year DESC "
