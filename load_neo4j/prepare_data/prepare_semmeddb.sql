CREATE TABLE entities(
    cui varchar(255),
    semtype varchar(50),
    name varchar(999),
    INDEX (cui)
);


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
