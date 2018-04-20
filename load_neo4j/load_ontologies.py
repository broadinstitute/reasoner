from owlready2 import *
onto_path.append("/data/owlready")
onto = get_ontology("http://purl.obolibrary.org/obo/hp.owl")
onto.load()

obo = onto.get_namespace("http://purl.obolibrary.org/obo/")

