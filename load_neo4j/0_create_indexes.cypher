//UmlsTerm
create index on :UmlsTerm(cui);
create constraint on (n:UmlsTerm) ASSERT n.cui is unique;

// Drug
create index on :Drug(drugbank_id);
create constraint on (n:Drug) ASSERT n.drugbank_id is unique;

create index on :Drug(chembl_id);
create constraint on (n:Drug) ASSERT n.chembl_id is unique;

create index on :Drug(cui);
create constraint on (n:Drug) ASSERT n.cui is unique;

create index on :Drug(chebi_id);
create constraint on (n:Drug) ASSERT n.chebi_id is unique;

create index on :Drug(name);


// Gene
create index on :Gene(hgnc_id);
create constraint on (n:Gene) ASSERT n.hgnc_id is unique;


// Protein
create index on :Protein(uniprot_id);
create constraint on (n:Protein) ASSERT n.uniprot_id is unique;
create index on :Protein(name);


// Target
create index on :Target(drugbank_id);
create constraint on (n:Target) ASSERT n.drugbank_id is unique;


// Pathway
create index on :Pathway(go_id);
create constraint on (n:Pathway) ASSERT n.go_id is unique;
create index on :Pathway(cui);
create constraint on (n:Pathway) ASSERT n.cui is unique;
create index on :Pathway(name);


// GoTerm
create index on :GoTerm(go_id);

create index on :GoTerm(cui);
create constraint on (n:GoTerm) ASSERT n.cui is unique;

create index on :GoTerm(name);


// Cell
create index on :Cell(cui);
create constraint on (n:Cell) ASSERT n.cui is unique;

create index on :Cell(name);


// Tissue
create index on :Tissue(cui);
create constraint on (n:Tissue) ASSERT n.cui is unique;

create index on :Tissue(name);


// Symptom
create index on :Symptom(cui);
create constraint on (n:Symptom) ASSERT n.cui is unique;

create index on :Symptom(name);


// Disease
create index on :Disease(cui);
create constraint on (n:Disease) ASSERT n.cui is unique;

create index on :Disease(hpo_id);
create constraint on (n:Disease) ASSERT n.hpo_id is unique;

create index on :Disease(mesh_id);
create constraint on (n:Disease) ASSERT n.mesh_id is unique;

create index on :Disease(name);



// HpoTerm
create index on :HpoTerm(hpo_id);
create constraint on (n:HpoTerm) ASSERT n.hpo_id is unique;

create index on :HpoTerm(cui);
create constraint on (n:HpoTerm) ASSERT n.cui is unique;

create index on :HpoTerm(name);


// UberonTerm
create index on :UberonTerm(uberon_id);
create constraint on (n:UberonTerm) ASSERT n.uberon_id is unique;

create index on :UberonTerm(cui);
create constraint on (n:UberonTerm) ASSERT n.cui is unique;

create index on :UberonTerm(name);
