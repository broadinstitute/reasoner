import mysql.connector
from .Config import Config
from .Dbtools import db_select


class SemmedDbTools:
    def __init__(self):
        config = Config().config
        self.db = mysql.connector.connect(user=config['semmeddb']['user'],
                                          password=config['semmeddb']['password'],
                                          host=config['semmeddb']['host'],
                                          database=config['semmeddb']['database'])

    def __del__(self):
        self.db.close()

    def get_terms(self):
        sql = ("SELECT cui, semtype, name "
               "FROM entities;")
        return(db_select(self.db, sql))

    def get_triples(self):
        sql = ("SELECT predicate, subject_cui, object_cui, count "
               "FROM PRED_SUMMARY "
               "WHERE count > 2 "
               "AND subject_cui != object_cui"
               "AND predicate NOT IN ('compared_with', 'higher_than', 'lower_than', 'different_from', 'NEG_higher_than', 'different_than');")
        return(db_select(self.db, sql))
