CREATE TABLE entities(
    cui varchar(255),
    semtype varchar(50),
    name varchar(999),
    INDEX (cui)
);

INSERT INTO entities (cui, semtype, name)
SELECT DISTINCT SUBJECT_CUI as cui, SUBJECT_SEMTYPE as semtype, SUBJECT_NAME as name
FROM PREDICATION
UNION
SELECT DISTINCT OBJECT_CUI as cui, OBJECT_SEMTYPE as semtype, OBJECT_NAME as name
FROM PREDICATION;
