import rdflib.term
from rdflib import Graph
from utilities import constants

def wanted_triplet(s, p, o):
    for unwanted in constants.UNWANTED:
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


def graph_bind(g_clean, namespaces=constants.NAMESPACES):

    for name, iri in namespaces.items():
        g_clean.bind(name, iri)


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
        if constants.TEXTUAL_REFERENCE_PREFIX in s:
            print(str(p))
            # text span
            if p == constants.LABEL_PREDICATE:
                enriching_triples_labels[str(s)] = ' '.join((o.split('^')[0]).split('_'))
            # individual referenced by text span
            if p == constants.DENOTE_PREDICATE:
                enriching_triples_individuals[str(s)] = o
            # class referenced by text span
            if p == constants.HAS_INTERPRETANT_PREDICATE:
                enriching_triples_classes[str(s)] = o
    # add triples found
    for key, label in enriching_triples_labels.items():
        individual_object = enriching_triples_individuals.get(key)
        if individual_object is not None:
            g_out.add((individual_object, constants.LABEL_PREDICATE, rdflib.Literal(label)))
            print(individual_object, " => ", label)
        class_object = enriching_triples_classes.get(key)
        if class_object is not None:
            g_out.add((class_object, constants.LABEL_PREDICATE, rdflib.Literal(label)))
            print(class_object, " => ", label)
    return g_out


def build_graph(path):
    g_raw = Graph()
    g_raw.parse(path, format="turtle")
    g_enriched = construct_text_references(g_raw)
    g_clean = clean_graph(g_enriched)
    graph_bind(g_clean)
    return g_clean
