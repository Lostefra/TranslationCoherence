import rdflib.term
from rdflib import Graph

TEXTUAL_REFERENCE_PREFIX = "offset_"
OFFSET_LABEL_PROPERTY = "http://www.w3.org/2000/01/rdf-schema#label"
DENOTE_PROPERTY = "http://ontologydesignpatterns.org/cp/owl/semiotics.owl#denotes"
HAS_INTERPRETANT_PROPERTY = "http://ontologydesignpatterns.org/cp/owl/semiotics.owl#hasInterpretant"
LABEL_PROPERTY = rdflib.term.URIRef("rdfs:label")
UNWANTED = ["http://www.ontologydesignpatterns.org/ont/fred/pos.owl",
            "http://ontologydesignpatterns.org/cp/owl/semiotics.owl",
            "http://www.essepuntato.it/2008/12/earmark",
            "http://www.ontologydesignpatterns.org/ont/cnlp/dependencies.owl",
            "http://www.ontologydesignpatterns.org/ont/vn/data",
            "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl",
            TEXTUAL_REFERENCE_PREFIX,
            "ObjectProperty"]


def wanted_triplet(s, p, o):
    for unwanted in UNWANTED:
        if unwanted in s or unwanted in p or unwanted in o:
            return False
    return True


def clean_graph(g_in):
    g_out = Graph()

    for s, p, o in g_in:
        if wanted_triplet(s, p, o):
            g_out.add((s, p, o))

    print(len(g_out.all_nodes()), "nodes in the cleaned graph")
    return g_out


def graph_bind(g_clean):
    g_clean.bind("fred", "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
    g_clean.bind("quant", "http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#")
    g_clean.bind("owl", "http://www.w3.org/2002/07/owl#")
    g_clean.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g_clean.bind("dul", "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
    g_clean.bind("vn.role", "http://www.ontologydesignpatterns.org/ont/vn/abox/role/")
    g_clean.bind("boxer", "http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#")
    g_clean.bind("dbpedia", "http://dbpedia.org/resource/")
    g_clean.bind("transl_coher", "http://example.org/translation_coherence/")


# add to each wanted element the related word (if exists)
# QUESTION: this function could encapsulate the cleaning?
def construct_text_references(g_in):
    g_out = Graph()
    # data structures that will store information about individual/class => text label
    enriching_triples_individuals = dict()
    enriching_triples_classes = dict()
    enriching_triples_labels = dict()
    for s, p, o in g_in:
        g_out.add((s, p, o))
        # check if the subject is an offset in the ontology and collect information about:
        # the expression and the individual and/or the class related
        if TEXTUAL_REFERENCE_PREFIX in s:
            # text span
            if str(p) == OFFSET_LABEL_PROPERTY:
                enriching_triples_labels[str(s)] = ' '.join((o.split('^')[0]).split('_'))
            # individual referenced by text span
            if str(p) == DENOTE_PROPERTY:
                enriching_triples_individuals[str(s)] = o
            # class referenced by text span
            if str(p) == HAS_INTERPRETANT_PROPERTY:
                enriching_triples_classes[str(s)] = o
    # add triples found
    for key, label in enriching_triples_labels.items():
        individual_object = enriching_triples_individuals.get(key)
        if individual_object is not None:
            g_out.add((individual_object, LABEL_PROPERTY, rdflib.Literal(label)))
            # print(individual_object, " => ", label)
        class_object = enriching_triples_classes.get(key)
        if class_object is not None:
            g_out.add((class_object, LABEL_PROPERTY, rdflib.Literal(label)))
            # print(class_object, " => ", label)
    return g_out


def build_graph(path):
    g_raw = Graph()
    g_raw.parse(path, format="turtle")
    g_enriched = construct_text_references(g_raw)
    g_clean = clean_graph(g_enriched)
    graph_bind(g_clean)
    return g_clean
