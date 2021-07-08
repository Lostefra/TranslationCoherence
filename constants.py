import rdflib

TEXTUAL_REFERENCE_PREFIX = "offset_"
LABEL_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label")
DENOTE_PREDICATE = rdflib.term.URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#denotes")
HAS_INTERPRETANT_PREDICATE = rdflib.term.URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#hasInterpretant")
SAME_AS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#sameAs")
EQUIVALENT_CLASS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#equivalentClass")
TYPE_PREDICATE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
UNWANTED = ["http://www.ontologydesignpatterns.org/ont/fred/pos.owl",
            "http://ontologydesignpatterns.org/cp/owl/semiotics.owl",
            "http://www.essepuntato.it/2008/12/earmark",
            "http://www.ontologydesignpatterns.org/ont/cnlp/dependencies.owl",
            "http://www.ontologydesignpatterns.org/ont/vn/data",
            # "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl",
            TEXTUAL_REFERENCE_PREFIX,
            "ObjectProperty"]
