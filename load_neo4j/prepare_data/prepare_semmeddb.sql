CREATE TABLE entities(
    cui varchar(255),
    semtype varchar(50),
    name varchar(999),
    INDEX (cui)
);

# TODO deal with ill-formatted cuis in semmeddb (separated by vertical bar | )
INSERT INTO semmeddb.entities (cui, semtype, name)
SELECT sdb.cui as cui, srdef.abr as semtype, sdb.name as name
FROM
(SELECT DISTINCT SUBJECT_CUI as cui, SUBJECT_NAME as name
FROM semmeddb.PREDICATION
UNION
SELECT DISTINCT OBJECT_CUI as cui, OBJECT_NAME as name
FROM semmeddb.PREDICATION) as sdb
INNER JOIN umls.MRSTY mrsty
ON sdb.cui = mrsty.cui
LEFT JOIN umls.SRDEF srdef on srdef.ui=mrsty.tui;



CREATE TABLE SEMTYPE_FILTERED(
	PREDICATION_ID INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (PREDICATION_ID)
);


INSERT INTO SEMTYPE_FILTERED (PREDICATION_ID)
SELECT PREDICATION_ID
FROM PREDICATION pred
INNER JOIN entities sub
ON sub.cui = pred.SUBJECT_CUI
AND sub.semtype = pred.SUBJECT_SEMTYPE
INNER JOIN entities obj
ON obj.cui = pred.OBJECT_CUI
AND obj.semtype = pred.OBJECT_SEMTYPE;



CREATE TABLE PRED_SUMMARY(
    predicate varchar(50),
    subject_cui varchar(255),
    object_cui varchar(255),
    count int(3) unsigned
);

INSERT INTO PRED_SUMMARY (predicate, subject_cui, object_cui, count)
SELECT predicate, subject_cui, object_cui, COUNT(*) as count
FROM PREDICATION
INNER JOIN SEMTYPE_FILTERED
ON SEMTYPE_FILTERED.PREDICATION_ID = PREDICATION.PREDICATION_ID
GROUP BY predicate, subject_cui, object_cui;
