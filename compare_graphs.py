from rdflib import Namespace, Graph
from build_graph import graph_bind
from utility_functions import is_class
from nltk.corpus import wordnet
import constants
from utility_functions import prefix, extracts_lemmas, index_generator, get_node_triples, get_word_synonyms, \
    get_class_name_from_iri
from pattern import negative_verbs, class_subclass_equivalence, find_synonyms, find_similar_words

THRESHOLD_SIMILARITY_SYNONYMY = 0.75


# TODO avoid alias if object / subjects are already the same
def sameAs_equivalentClass_transitivity(g1, g2, n, result_graph):
    # Check alias via "owl:sameAs" and "owl:equivalentClass", exploiting transitivity
    for s1, p1, o1 in g1:
        if prefix(p1, g1) == "owl:sameAs" or prefix(p1, g1) == "owl:equivalentClass":
            for s2, p2, o2 in g2:
                if prefix(s2, g2) == prefix(s1, g1) and (
                        prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((o2, n.alias, o1))
                elif prefix(s2, g2) == prefix(o1, g1) and (
                        prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((o2, n.alias, s1))
                elif prefix(o2, g2) == prefix(s1, g1) and (
                        prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((s2, n.alias, o1))
                elif prefix(o2, g2) == prefix(o1, g1) and (
                        prefix(p2, g2) == "owl:sameAs" or prefix(p2, g2) == "owl:equivalentClass"):
                    result_graph.add((s2, n.alias, s1))


def has_enough_matches(node, label, node_triples, g1, g2, lemmas):
    tot = 0
    new_starting_points = []
    for s1, p1, o1 in node_triples:
        label_subj = lemmas[str(g1.label(s1))]
        label_obj = lemmas[str(g1.label(o1))]

        if label_subj != "" and label_obj != "":
            for s2, p2, o2 in g2:
                if (label_subj, p1, label_obj) == (lemmas[str(g2.label(s2))], p2, lemmas[str(g2.label(o2))]):
                    if label == label_subj and not (o1, o2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((o1, o2))
                        break
                    elif label == label_obj and not (s1, s2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((s1, s2))
                        break
        elif label_subj == "" and label_obj != "" and is_class(s1, g1):
            for s2, p2, o2 in g2:
                if (s1, p1, label_obj) == (s2, p2, lemmas[str(g2.label(o2))]):
                    if node == s1 and not (o1, o2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((o1, o2))
                        break
                    elif label == label_obj and not (s1, s2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((s1, s2))
                        break
        elif label_subj != "" and label_obj == "" and is_class(o1, g1):
            for s2, p2, o2 in g2:
                if (label_subj, p1, o1) == (lemmas[str(g2.label(s2))], p2, o2):
                    if label == label_subj and not (o1, o2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((o1, o2))
                        break
                    elif node == o1 and not (s1, s2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((s1, s2))
                        break
        elif label_subj == "" and label_obj == "" and is_class(s1, g1) and is_class(o1, g1):
            for s2, p2, o2 in g2:
                if (s1, p1, o1) == (s2, p2, o2):
                    if node == s1 and not (o1, o2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((o1, o2))
                        break
                    elif node == o1 and not (s1, s2) in new_starting_points:
                        tot += 1
                        new_starting_points.append((s1, s2))
                        break

    if tot < 3:
        return []
    else:
        return new_starting_points


def get_other_centroid(node, label, g1, g2, lemmas):
    if label != "":
        for node_2 in g2.all_nodes():
            if label in lemmas[str(g2.label(node_2))]:
                return node_2
    elif label == "" and is_class(node, g1) and node in g2.all_nodes() and is_class(node, g2):
        # Return "node" since it is the same IRI of "node_2", so same object
        return node


def find_starting_points(g1, g2, lemmas, n, result_graph):
    # Mark as starting_points all the nodes which have enough relations equal in both graphs
    starting_points, equivalences_found_1, equivalences_found_2 = [], [], []
    '''
    # Find alias via "owl:sameAs" and "owl:equivalentClass", these predicates are in relation with dbpedia IRI
    # search for sameAs and equivalentClass to find equivalent objects in the two ontologies
    for property in (constants.SAME_AS_PREDICATE, constants.EQUIVALENT_CLASS_PREDICATE):
        g1_property, g2_property = g1.subject_objects(property), g2.subject_objects(property)
        for s1, o1 in g1_property:
            for s2, o2 in g2_property:
                if prefix(o2, g2) == prefix(o1, g1):
                    result_graph.add((s1, constants.SAME_AS_PREDICATE, s2))
                    starting_points.append((s1, s2))
                    equivalences_found_1 += [(s1, s2), (o1, o2)]
    '''
    for node in g1.all_nodes():
        if str(node).startswith(constants.QUANT_PREFIX) and node in g2.all_nodes() or \
                str(node).startswith(constants.DUL_PREFIX) and node in g2.all_nodes():
            starting_points = starting_points + [(node, node)]
        else:
            label = lemmas[str(g1.label(node))]
            # The centroid must have the same label in both graph, or must be the same class in both graph
            if (label != "" and label in [lemmas[str(g2.label(node_2))] for node_2 in g2.all_nodes()]) or \
                    (label == "" and is_class(node, g1) and node in g2.all_nodes() and is_class(node, g2)):
                # Get all g1 triples where node is present
                node_triples = get_node_triples(node, g1)
                # If the node has enough equal relations in both graphs, collect the relations' nodes
                new_starting_points = has_enough_matches(node, label, node_triples, g1, g2, lemmas)
                node_2 = get_other_centroid(node, label, g1, g2, lemmas)
                label_2 = lemmas[str(g2.label(node_2))]
                # Abort operation by setting empty "new_starting_points" if nodes are not both classes or both individuals, or if the have different labels or no labels and different IRI
                if (is_class(node, g1) and not is_class(node_2, g2)) or (not is_class(node, g1) and is_class(node_2, g2)) or \
                        (label != "" and label != label_2) or (label == "" and node != node_2):
                    new_starting_points = []
                if new_starting_points:
                    starting_points = starting_points + [(node, node_2)] + new_starting_points
                    # print(prefix(node, g1))
    # Remove duplicates
    # print(len(starting_points))
    starting_points = list(set(starting_points))
    # print(len(starting_points))
    for node in starting_points:
        # print(prefix(node[0], g1))
        result_graph.add((node[0], constants.STARTING_POINT_PREDICATE, node[1]))
    # print(starting_points)
    equivalences_found = list(map(list, zip(*starting_points)))
    if equivalences_found:
        equivalences_found_g1, equivalences_found_g2 = equivalences_found[0], equivalences_found[1]
    else:
        equivalences_found_g1, equivalences_found_g2 = [], []
    return set(starting_points), equivalences_found_g1, equivalences_found_g2


# return True if the 2 nodes from the 2 graphs received in input are considered equivalent
# (i.e they are connected with the same predicate, have the same lemma and are both individuals or class)
def check_nodes_equivalence(g1, g2, lemmas, node1, p1, node2, p2):
    # check if the two predicates are the same
    if p1 == p2 and p1 != constants.LABEL_PREDICATE:
        lemma1, lemma2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
        is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
        return (((not is_s1_class) and not is_s2_class) and lemma1 and lemma1 == lemma2) or \
                (is_s1_class and is_s2_class and node1 == node2)
    return False


# return True if two words are synonyms according to some rules that rely on Wordnet synsets and similarity metrics
def check_synonymy(word1, word2):
    if word1 in get_word_synonyms(word2):
        return True
    # otherwise compute the max similarity between all possible synsest (using path and wup similarity)
    similarity = 0
    # for each pair of synset compute the similarity and find the maximum
    for synset1 in wordnet.synsets(word1):
        for synset2 in wordnet.synsets(word2):
            new_similarity = 0.33 * synset1.path_similarity(synset2) + 0.67 * synset1.wup_similarity(synset2)
            similarity = max(similarity, new_similarity) if word1 and word2 else 0
    # the two words are synonyms if the similarity is above a certain threshold
    return similarity > THRESHOLD_SIMILARITY_SYNONYMY


# return True if the 2 nodes from the 2 graphs received in input are considered equivalent
# (i.e they are connected with the same predicate, have the same lemma and are both individuals or class)
def check_nodes_synonymy(g1, g2, lemmas, node1, p1, node2, p2):
    # check if the two predicates are the same
    if p1 == p2 and p1 != constants.LABEL_PREDICATE:
        wordnet_lemmas = set(wordnet.all_lemma_names())
        is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
        if (not is_s1_class) and (not is_s2_class):
            word1, word2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
            if word1 in wordnet_lemmas and word2 in wordnet_lemmas:
                return check_synonymy(word1, word2)
        elif is_s1_class and is_s2_class:
            expression1, expression2 = get_class_name_from_iri(str(node1)), get_class_name_from_iri(str(node2))
            expression1 = [word for word in expression1.split(" ")]
            expression2 = [word for word in expression2.split(" ")]
            if len(expression1) == len(expression2):
                for word1, word2 in zip(expression1, expression2):
                    if word1 != word2 or not check_synonymy(word1, word2):
                        return False
                return True
    return False


# connect 2 elements with a certain predicate
def add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, nodes_classified_g1,
                                      nodes_classified_g2, predicate):
    if predicate is not None:
        result_graph.add((node1, predicate, node2))
    new_frontiers.add((node1, node2))
    nodes_classified_g1.append(node1)
    nodes_classified_g2.append(node2)


def add_equivalence_relation(node1, node2, result_graph, new_frontiers, nodes_classified_g1, nodes_classified_g2):
    add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, nodes_classified_g1,
                                      nodes_classified_g2, constants.EQUIVALENCE_PREDICATE)


def add_synonymy_relation(node1, node2, result_graph, new_frontiers, nodes_classified_g1, nodes_classified_g2):
    add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, nodes_classified_g1,
                                      nodes_classified_g2, constants.SYNONYMY_PREDICATE)


def find_equivalence_relations(g1, g2, lemmas, n, result_graph, starting_points, new_frontiers, nodes_classified_g1,
                               nodes_classified_g2):
    return find_binary_relation(g1, g2, lemmas, n, result_graph, starting_points, new_frontiers, nodes_classified_g1,
                                nodes_classified_g2, check_nodes_equivalence, add_equivalence_relation)


def find_synonymy_relations(g1, g2, lemmas, n, result_graph, starting_points, new_frontiers, nodes_classified_g1,
                            nodes_classified_g2):
    return find_binary_relation(g1, g2, lemmas, n, result_graph, starting_points, new_frontiers, nodes_classified_g1,
                                nodes_classified_g2, check_nodes_synonymy, add_synonymy_relation)


# DONE:
# We keep tracks of the equivalent nodes and the frontier's nodes. In such a way we'll just check the variations classes
# on the neighbours nodes of the frontier's nodes, and compare just the potential differences (both for correctness and
# efficiency). As soon the variation is classified, then we restarted the equivalence propagation until it stops; then
# variation classification and so on and so forth until all the nodes are evaluated.
def find_binary_relation(g1, g2, lemmas, n, result_graph, starting_points, new_frontiers, nodes_classified_g1,
                         nodes_classified_g2, binary_relation_condition, binary_relation_action):
    # for each pair of starting_points see if in the two ontologies there are predicate-object or subject-predicate
    # "equal" according to some criteria, and propagate the equivalence
    # the starting pair is the equivalence found before
    found = False
    for elem1, elem2 in starting_points:
        # check if a predicate-object equivalent pair exists
        for p1, o1 in g1.predicate_objects(elem1):
            for p2, o2 in g2.predicate_objects(elem2):
                if p1 != constants.TYPE_PREDICATE and p2 != constants.TYPE_PREDICATE and \
                        (o1 not in nodes_classified_g1) and (o2 not in nodes_classified_g2):
                    if binary_relation_condition(g1, g2, lemmas, o1, p1, o2, p2):
                        binary_relation_action(o1, o2, result_graph, new_frontiers, nodes_classified_g1,
                                               nodes_classified_g2)
                        found = True
        # check if a subject-predicate equivalent pair exists
        for s1, p1 in g1.subject_predicates(elem1):
            for s2, p2 in g2.subject_predicates(elem2):
                if p1 != constants.TYPE_PREDICATE and p2 != constants.TYPE_PREDICATE and \
                            (s1 not in nodes_classified_g1) and (s2 not in nodes_classified_g2):
                    if binary_relation_condition(g1, g2, lemmas, s1, p1, s2, p2):
                        binary_relation_action(s1, s2, result_graph, new_frontiers, nodes_classified_g1,
                                               nodes_classified_g2)
                        found = True
    return found


def compare_graphs(g1, g2):
    n = Namespace("http://example.org/translation_coherence/")
    result_graph = Graph()
    indexes = {}
    for name in ["expressions"]:
        indexes[name] = index_generator()

    lemmas = extracts_lemmas(g1, g2)

    # INVESTIGATE SYNONYMY AND SIMILARITIES BETWEEN WORDS
    # print("-" * 150)  # #########################################################
    # print("WordNet (synset)")
    # print(find_synonyms(g1, g2, lemmas))
    # print("-" * 150)  # #########################################################
    # print("WordNet (path_similarity)")
    # print(find_similar_words(g1, g2, lemmas, "path", 0.45, "max"))
    # print("-" * 150)  # #########################################################
    # print("WordNet (lch_similarity)")
    # print(find_similar_words(g1, g2, lemmas, "lch", 0.5, "max"))
    # print("-" * 150)  # #########################################################
    # print("WordNet (wup_similarity)")
    # print(find_similar_words(g1, g2, lemmas, "wup", 0.85, "max"))
    # print("-" * 150)  # #########################################################
    # print("WordNet (combine similarity)")
    # print(find_similar_words(g1, g2, lemmas, "combination", 0.75, "max"))
    # print("-" * 150)  # #########################################################
    # print("GloVe")
    # synonyms2(g1, g2, n, result_graph)
    # print("-" * 150)  # #########################################################

    # EXPLORING THE GRAPH FOR FINDING RELATIONS

    # Populate result_graph by recognizing patterns on g1, g2
    # print("-" * 150)  # #########################################################
    # print("sameAs_equivalentClass_transitivity")
    # sameAs_equivalentClass_transitivity(g1, g2, n, result_graph)
    # print("-" * 150)  # #########################################################

    # starting_points are nodes from which propagate the equivalences
    # equivalences_found are nodes which have a correspondence in both the graphs
    frontiers, equivalences_found_g1, equivalences_found_g2 = find_starting_points(g1, g2, lemmas, n, result_graph)
    all_frontiers = frontiers.copy()
    while len(frontiers) > 0:
        new_frontiers = set()

        print("find equivalence")
        while (find_equivalence_relations(g1, g2, lemmas, n, result_graph, frontiers, new_frontiers,
                                          equivalences_found_g1, equivalences_found_g2)):
            pass
        find_synonymy_relations(g1, g2, lemmas, n, result_graph, frontiers, new_frontiers, equivalences_found_g1,
                                equivalences_found_g2)
        print("-" * 150)  # #########################################################
        print("negative verbs")
        negative_verbs(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers, mode=1)
        negative_verbs(g2, g1, n, result_graph, indexes, lemmas, frontiers, new_frontiers, mode=2)
        # print("DBPedia equivalence")
        # dbpedia_equivalence(g1, g2, n, result_graph)
        print("-" * 150)  # #########################################################
        # print("class_subclass_equivalence")
        # class_subclass_equivalence(g1, g2, lemmas, n, result_graph, frontiers)
        # print("-" * 150)  # #########################################################

        new_frontiers -= all_frontiers

        frontiers = new_frontiers.copy()
        all_frontiers = all_frontiers.union(new_frontiers)
        print("-" * 150)  # #########################################################

    graph_bind(result_graph)
    return result_graph
