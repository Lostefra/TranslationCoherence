import os
import utilities.constants as constants
import spacy
from rdflib.term import Literal, URIRef
from utilities.wordnet_utility_functions import check_synonymy
from nltk.corpus import wordnet
import re

nlp_analyzer = spacy.load('en_core_web_sm')
THRESHOLD_COMMON_NEIGHBOURS_FOR_BINARY_DIFFERENCE = 2


def pad_prefix(el, graph):
    return "{:<50}".format(el.n3(graph.namespace_manager))


def prefix(el, graph):
    return pad_prefix(el, graph).strip()


def change_prefix(node, new_prefix):
    tmp = "/"
    if new_prefix[-1] == '/':
        tmp = ""
    if '#' in str(node):
        return URIRef(new_prefix + tmp + str(node).split("#")[-1])
    else:
        return URIRef(new_prefix + tmp + str(node).split("/")[-1])


def word(el, graph):
    return prefix(el, graph).split(":")[1].lower().translate({ord(x): '' for x in "_1234567890"})


def index_generator():
    num = 1
    while True:
        yield str(num)
        num += 1


def extract_words(g):
    words = set()
    rex = re.compile("_[0-9]+$")
    for s, p, o in g:
        if rex.search(prefix(s, g)):
            if word(s, g) != "situation":
                words.add((s, word(s, g)))
        if rex.search(prefix(o, g)) or prefix(p, g) == "dul:hasQuality":
            if word(o, g) != "situation":
                words.add((o, word(o, g)))
    return words


def lemma(text):
    if isinstance(text, Literal):
        text = str(text)
    return " ".join([token.lemma_ for token in nlp_analyzer(text)])


# receives N graphs in input and return a dictionary with the form "label" => label's lemma
def extracts_lemmas(*args):
    lemmas = dict()
    for g in args:
        # get all the nodes of the graph
        nodes = g.all_nodes()
        for elem in nodes:
            label = str(g.label(elem))
            if label != '' and label not in lemmas:
                lemmas[label] = lemma(label)
    lemmas[""] = ''
    return lemmas


def is_class(obj, graph):
    is_explicit_class = graph.value(subject=obj, predicate=constants.TYPE_PREDICATE, default=None) == constants.CLASS_OBJECT
    is_subclass_of = graph.value(subject=obj, predicate=constants.SUBCLASS_PREDICATE, default=None) is not None
    is_type_of = graph.value(object=obj, predicate=constants.TYPE_PREDICATE, default=None) is not None
    return is_explicit_class or is_subclass_of or is_type_of


def get_node_triples(node, g):
    result = []
    for s, p, o in g:
        if (s == node or o == node) and p != constants.LABEL_PREDICATE:
            result.append((s, p, o))
    return result


def get_class_name_from_iri(class_iri_string):
    name = ""
    for char in class_iri_string.split('#')[-1]:
        if char.isupper() and name != "":
            name += " "
        name += char
    return name.lower()


# return True if the 2 nodes from the 2 graphs received in input are considered equivalent
# (i.e have the same lemma and are both individuals or class)
def check_nodes_equivalence(g1, g2, lemmas, node1, node2):
    lemma1, lemma2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
    is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
    return (((not is_s1_class) and not is_s2_class) and lemma1 and lemma1 == lemma2) or \
           (is_s1_class and is_s2_class and get_class_name_from_iri(node1) == get_class_name_from_iri(node2)) or \
           (isinstance(node1, Literal) and isinstance(node1, Literal) and node1 == node2)


# return True if the 2 nodes from the 2 graphs received in input are considered equivalent
# (i.e they are connected with the same predicate, have the same lemma and are both individuals or class)
def check_nodes_synonymy(g1, g2, lemmas, node1, node2):
    wordnet_lemmas = set(wordnet.all_lemma_names())
    is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
    if (not is_s1_class) and (not is_s2_class):
        word1, word2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
        # check if the words are in the wordnet dictionary
        if word1 in wordnet_lemmas and word2 in wordnet_lemmas:
            return check_synonymy(word1, word2)
    elif is_s1_class and is_s2_class:
        expression1, expression2 = get_class_name_from_iri(str(node1)), get_class_name_from_iri(str(node2))
        expression1 = [word for word in expression1.split(" ")]
        expression2 = [word for word in expression2.split(" ")]
        if len(expression1) == len(expression2):
            for word1, word2 in zip(expression1, expression2):
                if word1 != word2 and not check_synonymy(word1, word2):
                    return False
            return True
    return False


def check_nodes_binary_difference(g1, g2, lemmas, node1, node2):
    return lemma(g1.label(node1)) != lemma(g2.label(node2)) and \
           check_common_neighbourhood(g1, g2, lemmas, node1, node2, THRESHOLD_COMMON_NEIGHBOURS_FOR_BINARY_DIFFERENCE)


# check if two different nodes seems to play the same role in the ontology (i.e. surrounded by similar objects)
def check_common_neighbourhood(g1, g2, lemmas, node1, node2, threshold=2):
    if check_nodes_equivalence(g1, g2, lemmas, node1, node2):
        return False
    equivalent_neighbour_counter = 0
    # check if a predicate-object equivalent pair exists
    for p1, o1 in g1.predicate_objects(node1):
        for p2, o2 in g2.predicate_objects(node2):
            if p1 == p2 and check_nodes_equivalence(g1, g2, lemmas, o1, o2):
                equivalent_neighbour_counter += 1
    # check if a subject-predicate equivalent pair exists
    for s1, p1 in g1.subject_predicates(node1):
        for s2, p2 in g2.subject_predicates(node2):
            if p1 == p2 and check_nodes_equivalence(g1, g2, lemmas, s1, s2):
                equivalent_neighbour_counter += 1
    return equivalent_neighbour_counter >= threshold


# connect 2 elements with a certain predicate
def add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, predicate):
    if predicate is not None:
        result_graph.add((node1, predicate, node2))
    new_frontiers.add((node1, node2))


def add_equivalence_relation(node1, node2, result_graph, new_frontiers):
    add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, constants.EQUIVALENCE_PREDICATE)


def add_synonymy_relation(node1, node2, result_graph, new_frontiers):
    add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, constants.SYNONYMY_PREDICATE)


def add_binary_difference_relation(node1, node2, result_graph, new_frontiers):
    add_binary_relation_across_graphs(node1, node2, result_graph, new_frontiers, constants.GENERIC_DIFFERENCE_PREDICATE)


def equivalence_classified(node1, node2, result_graph):
    return (node1, constants.EQUIVALENCE_PREDICATE, node2) in result_graph


def synonymy_classified(node1, node2, result_graph):
    return (node1, constants.SYNONYMY_PREDICATE, node2) in result_graph


def difference_classified(node1, node2, result_graph):
    return (node1, constants.GENERIC_DIFFERENCE_PREDICATE, node2) in result_graph


def check_valid_ontology(file_path):
    valid = True
    http_error_500 = "<h2>HTTP ERROR: 500</h2>"
    ontology_file = open(file_path, "r")
    file_content = ontology_file.read()
    if file_content == "":
        valid = False
    if http_error_500 in file_content:
        valid = False
    return valid


def get_ids_valid_ontologies(folders):
    valid_ids = set()
    first = True
    for folder in folders:
        ontologies = os.listdir(folder)
        for ontology in ontologies:
            id_sentence = int(ontology.split("sentence")[1].split(".")[0])
            if first and check_valid_ontology(folder + ontology):
                valid_ids.add(id_sentence)
            if not first and not check_valid_ontology(folder + ontology):
                if id_sentence in valid_ids:
                    valid_ids.remove(id_sentence)
        first = False
    return sorted(list(valid_ids))


def get_categories_from_range(lengths, groups):
    x = []
    for i, upper_bound in enumerate(groups):
        if not len(x):
            x.append(str(min(lengths)) + "-" + str(upper_bound))
        else:
            x.append(str(groups[i - 1] + 1) + "-" + str(upper_bound))
    return x