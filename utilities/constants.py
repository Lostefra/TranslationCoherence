import rdflib

TEXTUAL_REFERENCE_PREFIX = "offset_"
LABEL_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label")
DENOTE_PREDICATE = rdflib.term.URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#denotes")
HAS_INTERPRETANT_PREDICATE = rdflib.term.URIRef(
    "http://ontologydesignpatterns.org/cp/owl/semiotics.owl#hasInterpretant")
SAME_AS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#sameAs")
EQUIVALENT_CLASS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#equivalentClass")

EQUIVALENCE_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/equivalent')
STARTING_POINT_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/starting_point')
SYNONYMY_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/synonymy')
GENERIC_DIFFERENCE_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/different')

TYPE_PREDICATE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
CLASS_OBJECT = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')
SUBCLASS_PREDICATE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf')

NAMESPACES = {
    'fred': 'http://www.ontologydesignpatterns.org/ont/fred/domain.owl#',
    'quant': 'http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dul': 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#',
    'vn.role': 'http://www.ontologydesignpatterns.org/ont/vn/abox/role/',
    'boxer': 'http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#',
    'boxing': 'http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#',
    'dbpedia': 'http://dbpedia.org/resource/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'schema': 'http://schema.org/',
    'coref': 'http://www.ontologydesignpatterns.org/ont/cnlp/coref.owl#',
    'time': 'http://www.w3.org/2006/time#',
    'transl_coher': 'http://example.org/translation_coherence/',
    'transl_coher_final': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/',
    # THE FOLLOWING PREFIXES ARE MADE FOR DEBUG REASONS
    'tc_vocabulary': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/vocabulary/',
    'en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence2/',
    'en_it_en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence2/',
}
UNWANTED = ["http://www.ontologydesignpatterns.org/ont/fred/pos.owl",
            "http://ontologydesignpatterns.org/cp/owl/semiotics.owl",
            "http://www.essepuntato.it/2008/12/earmark",
            "http://www.ontologydesignpatterns.org/ont/cnlp/dependencies.owl",
            "http://www.ontologydesignpatterns.org/ont/vn/data",
            # "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl",
            TEXTUAL_REFERENCE_PREFIX,
            "ObjectProperty"]
QUANT_PREFIX = NAMESPACES['quant']
DUL_PREFIX = NAMESPACES['dul']
BOXING_PREFIX = NAMESPACES["boxing"]
