//UmlsTerm
create constraint on (n:UmlsTerm) ASSERT n.cui is unique;

// Drug
create constraint on (n:Drug) ASSERT n.drugbank_id is unique;
create constraint on (n:Drug) ASSERT n.chembl_id is unique;
create constraint on (n:Drug) ASSERT n.cui is unique;
create constraint on (n:Drug) ASSERT n.chebi_id is unique;
create index on :Drug(name);


// Gene
create constraint on (n:Gene) ASSERT n.hgnc_id is unique;


// Protein
create constraint on (n:Protein) ASSERT n.uniprot_id is unique;
create index on :Protein(name);


// Target
create constraint on (n:Target) ASSERT n.drugbank_id is unique;


// Pathway
create constraint on (n:Pathway) ASSERT n.go_id is unique;
create constraint on (n:Pathway) ASSERT n.cui is unique;
create index on :Pathway(name);


// GoTerm
create constraint on (n:GoTerm) ASSERT n.cui is unique;
create index on :GoTerm(go_id);
create index on :GoTerm(name);


// Cell
create constraint on (n:Cell) ASSERT n.cui is unique;
create index on :Cell(name);


// Tissue
create constraint on (n:Tissue) ASSERT n.cui is unique;
create index on :Tissue(name);


// Symptom
create constraint on (n:Symptom) ASSERT n.cui is unique;
create index on :Symptom(name);


// Disease
create constraint on (n:Disease) ASSERT n.cui is unique;
create constraint on (n:Disease) ASSERT n.hpo_id is unique;
create constraint on (n:Disease) ASSERT n.mesh_id is unique;
create index on :Disease(name);



// HpoTerm
create constraint on (n:HpoTerm) ASSERT n.hpo_id is unique;
create constraint on (n:HpoTerm) ASSERT n.cui is unique;
create index on :HpoTerm(name);


// UberonTerm
create constraint on (n:UberonTerm) ASSERT n.uberon_id is unique;
create constraint on (n:UberonTerm) ASSERT n.cui is unique;
create index on :UberonTerm(name);
