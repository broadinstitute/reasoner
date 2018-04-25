create index on :Drug(drugbank_id);
create index on :Drug(chembl_id);
create index on :Drug(cui);
create index on :Drug(chebi_id);
create index on :Drug(name);

create index on :Target(drugbank_id);
create index on :Target(hgnc_id);
create index on :Target(uniprot_id);
create index on :Target(name);

create index on :Pathway(go_id);
create index on :Pathway(cui);
create index on :Pathway(name);

create index on :Cell(cui);
create index on :Cell(name);

create index on :Tissue(cui);
create index on :Tissue(name);

create index on :Symptom(cui);
create index on :Symptom(name);

create index on :Disease(cui);
create index on :Disease(name);
