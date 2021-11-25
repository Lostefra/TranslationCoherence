import rdflib

TEXTUAL_REFERENCE_PREFIX = "offset_"
HAS_CONTENT_PREDICATE = rdflib.term.URIRef('http://www.essepuntato.it/2008/12/earmark#hasContent')
LABEL_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label")
DENOTE_PREDICATE = rdflib.term.URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#denotes")
HAS_INTERPRETANT_PREDICATE = rdflib.term.URIRef(
    "http://ontologydesignpatterns.org/cp/owl/semiotics.owl#hasInterpretant")
SAME_AS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#sameAs")
EQUIVALENT_CLASS_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#equivalentClass")

EQUIVALENCE_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/equivalent')
STARTING_POINT_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/stronglyEquivalent')
SYNONYMY_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/synonymy')
GENERIC_DIFFERENCE_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/different')
DIFFERENT_CONTEXT_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/differentContext')
ONLY_IN_PREDICATE = rdflib.term.URIRef('http://example.org/translation_coherence/onlyIn')

TYPE_PREDICATE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
CLASS_OBJECT = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')
SUBCLASS_PREDICATE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf')

# Semantic types used for statistical analysis
SEMANTIC_TYPES_PREFIXES = ["http://www.ontologydesignpatterns.org/ont/dul/DUL.owl",
"http://www.ontologydesignpatterns.org/ont/d0.owl", "http://schema.org/"]
SEMANTIC_TYPES = ['http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Event',
                  'http://www.ontologydesignpatterns.org/ont/d0.owl#Activity',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Situation',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Quality',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#InformationEntity',
                  'http://www.ontologydesignpatterns.org/ont/d0.owl#Topic',
                  'http://www.ontologydesignpatterns.org/ont/d0.owl#Location',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#PhysicalObject',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Description',
                  'http://www.ontologydesignpatterns.org/ont/d0.owl#Characteristic',
                  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#TimeInterval']
SEMANTIC_METRIC_PREDICATES = [EQUIVALENCE_PREDICATE, SYNONYMY_PREDICATE, GENERIC_DIFFERENCE_PREDICATE,
                              DIFFERENT_CONTEXT_PREDICATE, ONLY_IN_PREDICATE]


NAMESPACES = {
    'fred': 'http://www.ontologydesignpatterns.org/ont/fred/domain.owl#',
    'quant': 'http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'dul': 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#',
    'vn.role': 'http://www.ontologydesignpatterns.org/ont/vn/abox/role/',
    'boxer': 'http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#',
    'boxing': 'http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#',
    'dbpedia': 'http://dbpedia.org/resource/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'earmark': 'http://www.essepuntato.it/2008/12/earmark#',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'schema': 'http://schema.org/',
    'coref': 'http://www.ontologydesignpatterns.org/ont/cnlp/coref.owl#',
    'time': 'http://www.w3.org/2006/time#',
    'transl_coher': 'http://example.org/translation_coherence/',
    'translation_coherence': 'https://w3id.org/stlab/ke/amiala/',
    'translation_coherence_vocabulary': 'https://w3id.org/stlab/ke/amiala/translation_coherence/',
    # THE FOLLOWING PREFIXES ARE MADE FOR DEBUG REASONS
    # Sentence 1
    # 'en_sentence1': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence1/',
    # 'en_it_en_sentence1': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence1/',
    # Sentence 2
    # 'en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence2/',
    # 'en_it_en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence2/',
    # 'en_de_en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence2/',
    #'en_cn_en_sentence2': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence2/',
    # Sentence 3
    # 'en_sentence3': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence3/',
    # 'en_it_en_sentence3': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence3/',
    # # Sentence 4
    #'en_sentence4': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence4/',
    #'en_it_en_sentence4': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence4/',
    # # Sentence 5
    # 'en_sentence5': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence5/',
    # 'en_it_en_sentence5': 'https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence5/',
}
IMPORTED_ONTOLOGIES = ['quant', 'owl', 'rdf', 'rdfs', 'dul', 'vn.role', 'boxer', 'boxing', 'dbpedia', 'foaf', 'schema', 'coref', 'time']
UNWANTED = ["http://www.ontologydesignpatterns.org/ont/fred/pos.owl",
            "http://ontologydesignpatterns.org/cp/owl/semiotics.owl",
            "http://www.essepuntato.it/2008/12/earmark",
            "http://www.ontologydesignpatterns.org/ont/cnlp/dependencies.owl",
            "http://www.ontologydesignpatterns.org/ont/vn/data",
            "http://www.w3.org/2006/03/wn",
            # "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl",
            TEXTUAL_REFERENCE_PREFIX,
            "ObjectProperty"]

CLASS_CONCEPT_CLASS = rdflib.term.URIRef(NAMESPACES["translation_coherence_vocabulary"] + "ClassConcept")
SEE_ALSO_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#seeAlso")
DISJOINT_WITH_PREDICATE = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#disjointWith")
PARENT_CLASS_CONCEPT_PREDICATE = rdflib.term.URIRef(NAMESPACES["translation_coherence_vocabulary"] + "parentClassConcept")


QUANT_PREFIX = NAMESPACES['quant']
DUL_PREFIX = NAMESPACES['dul']
BOXING_PREFIX = NAMESPACES["boxing"]
OWL_PREFIX = NAMESPACES["owl"]
VNROLE_PREFIX = NAMESPACES["vn.role"]
DBPEDIA_PREFIX = NAMESPACES["dbpedia"]
