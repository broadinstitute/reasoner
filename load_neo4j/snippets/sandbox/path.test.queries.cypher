match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell) return count(*)
match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue) return count(*)

# get number of full cop cycles
match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s) return count(*)

# show all diseases that have full cop cycles
match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s) return distinct di.name

# get drugs with cop cycles for Malaria
match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s), (di)-[:HAS_SYNONYM]->(:Synonym {name:'Hay fever'}) return distinct dr.name




# get number of full cop cycles
match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di) return count(*)

# show all diseases that have full cop cycles
match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di) return distinct di.name

# get drugs with cop cycles for disease
match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di), (di)-[:HAS_SYNONYM]->(:Synonym {name:'Heart failure'}) return distinct dr.name


# get cop cycles for drug and disease
match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di), (di)-[:HAS_SYNONYM]->(:Synonym {name:'Heart failure'}), (dr)-[:HAS_SYNONYM]->(:Synonym {name: 'Nitrogen'}) return distinct di,dr,ta,p,c,ti limit 300


match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di) where (di)-[:HAS_SYNONYM]->(:Synonym {name:'Heart failure'}) and (dr)-[:HAS_SYNONYM]->(:Synonym {name: 'Captopril'}) return distinct di,dr,ta,p,c,ti limit 300


match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di) where di.name='Heart failure' and (dr)-[:HAS_SYNONYM]->(:Synonym {name: 'Sodium nitrite'}) and ti.name = 'Entire atrium' return distinct di,dr,ta,p,c,ti limit 300





match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di), (di)--(p), (di)--(c) return distinct di.name

match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di), (di)--(p), (di)--(c) where (di)-[:HAS_SYNONYM]->(:Synonym {name:'Hypertensive disease'}) return distinct di,dr,ta,p,c,ti limit 300




match (di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(di), (di)--(p), (di)--(c), (ti)--(p) return distinct di.name



match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s) return dr,count(*)

 match (s:Symptom)--(di:Disease)--(dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s) where (dr)-[:HAS_SYNONYM]->(:Synonym {name: 'Pantoprazole'}) return s,di,dr,ta,p,c,ti


 match (dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s:Symptom)--(di:Disease)--(dr) where (di)-[:HAS_SYNONYM]->(:Synonym {name: 'Multiple Myeloma'}) return s,di,dr,ta,p,c,ti

 match (dr:Drug)--(ta:Target)--(p:Pathway)--(c:Cell)--(ti:Tissue)--(s:Symptom)--(di:Disease)--(dr) return di,count(*) as n_paths order by n_paths desc