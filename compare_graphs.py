from rdflib import Namespace, Graph, term
from build_graph import graph_bind

import constants


from pattern import negative_verbs, dbpedia_equivalence, find_synonyms, prefix, index_generator


# TODO avoid alias if object / subjects are already the same
def sameAs_equivalentClass_transitivity(g1, g2, n, result_graph):
    # Check alias via "owl:sameAs" and "owl:equivalentClass", exploiting transitivity
    for s1, p1, o1 in g1:
        if prefix(p1, g1) == "owl:sameAs" or prefix(p1, g1) == "owl:equivalentClass":
            for s2, p2, o2 in g2:
                if prefix(s2, g2) == prefix(s1, g1) and (prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((o2, n.alias, o1))
                elif prefix(s2, g2) == prefix(o1, g1) and (prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((o2, n.alias, s1))
                elif prefix(o2, g2) == prefix(s1, g1) and (prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((s2, n.alias, o1))
                elif prefix(o2, g2) == prefix(o1, g1) and (prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((s2, n.alias, s1))


# TODO:
#  1) add checks for instances (i.e. propagate the equivalence only if there exists
#       a single individual for the class, for example)
#  2) add more starting point (not just sameAs and equivalentClass)
#  3) decide how to handle equivalence:
#       a) remove triples
#       b) adding connection
#       c) (this doesn't exclude the previous two, but probably needed) keep tracks of the equivalent nodes and the
#           frontier's nodes. In such a way we'll just check the variations classes on the neighbours nodes of the
#           frontier's nodes, and compare just the potential differences (both for correctness and efficiency). As soon
#           the variation is classified, then we restarted the equivalence propagation until it stops; then variation
#           classification and so on and so forth until all the nodes are evaluated.
def find_equivalence(g1, g2, n, result_graph):
    # Check alias via "owl:sameAs" and "owl:equivalentClass", exploiting a lot of stuff
    nodes_to_expand_queue = []
    alias_found = []
    # search for sameAs and equivalentClass to find equivalent objects in the two ontologies
    for property in (constants.SAME_AS_PREDICATE, constants.EQUIVALENT_CLASS_PREDICATE):
        g1_property, g2_property = g1.subject_objects(property), g2.subject_objects(property)
        for s1, o1 in g1_property:
            for s2, o2 in g2_property:
                if prefix(o2, g2) == prefix(o1, g1):
                    result_graph.add((s1, constants.SAME_AS_PREDICATE, s2))
                    # result_graph.remove((s1, property, o1))
                    # result_graph.remove((s2, property, o2))
                    # print("Equivalent:\n\t", s1, " ", property, " ", o1, "\n\t", s2, " ", property, " ", o2)
                    nodes_to_expand_queue.append((s1, s2))
                    alias_found = [(s1, s2), (o1, o2)]
    # the pair just found will be the starting point for the search:
    # for each pair see if in the two ontologies there are predicate-object or subject-predicate
    # "equal" according to some criteria, and propagate the equivalence
    # the starting pair is the equivalence found before
    while len(nodes_to_expand_queue):
        elem1, elem2 = nodes_to_expand_queue.pop(0)
        # check if a predicate-object equivalent pair exists
        for p1, o1 in g1.predicate_objects(elem1):
            for p2, o2 in g2.predicate_objects(elem2):
                # if "bug_1" in str(elem1):
                #     print("1: ", s1, p1, elem1)
                #     print("2: ", s2, p2, elem2)
                if (o1, o2) not in alias_found and prefix(p1, g1) == prefix(p2, g2) and p1 != constants.LABEL_PREDICATE \
                        and prefix(o1, g1) == prefix(o2, g2):
                    result_graph.add((o1, constants.SAME_AS_PREDICATE, o2))
                    # result_graph.remove((elem1, p1, o1))
                    # result_graph.remove((elem2, p2, o2))
                    # print("Equivalent:\n\t", elem1, " ", p1, " ", o1, "\n\t", elem2, " ", p2, " ", o2)
                    nodes_to_expand_queue.append((o1, o2))
                    alias_found.append((o1, o2))
        # check if a subject-predicate equivalent pair exists
        for s1, p1 in g1.subject_predicates(elem1):
            for s2, p2 in g2.subject_predicates(elem2):
                if (s1, s2) not in alias_found and prefix(p1, g1) == prefix(p2, g2) and p1 != constants.LABEL_PREDICATE \
                        and prefix(s1, g1) == prefix(s2, g2):
                    # check if the labels are equal
                    # label1 = g1.value(subject=s1, predicate=LABEL_PREDICATE, default=0)
                    # label2 = g2.value(subject=s2, predicate=LABEL_PREDICATE, default=0)
                    # if label1 and label2 and label1 == label2:
                    result_graph.add((s1, constants.SAME_AS_PREDICATE, s2))
                    # result_graph.remove((s1, p1, elem1))
                    # result_graph.remove((s2, p2, elem2))
                    # print("Equivalent:\n\t", s1, " ", p1, " ", elem1, "\n\t", s2, " ", p2, " ", elem2)
                    nodes_to_expand_queue.append((s1, s2))
                    alias_found.append((s1, s2))


def compare_graphs(g1, g2):
    n = Namespace("http://example.org/translation_coherence/")
    result_graph = Graph()
    indexes = {}
    for name in ["expressions"]:
        indexes[name] = index_generator()

    # Populate result_graph by recognizing patterns on g1, g2
    print("-" * 150)  # #########################################################
    print("sameAs_equivalentClass_transitivity")
    # sameAs_equivalentClass_transitivity(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("find equivalence")
    find_equivalence(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("negative verbs")
    negative_verbs(g1, g2, n, result_graph, indexes)
    negative_verbs(g2, g1, n, result_graph, indexes)
    print("-" * 150)  # #########################################################
    print("WordNet (synset)")
    find_synonyms(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("WordNet (wup_similarity)")
    # synonyms1(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("GloVe")
    # synonyms2(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("DBPedia equivalence")
    dbpedia_equivalence(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################

    graph_bind(result_graph)
    return result_graph
