import utilities.constants as constants
import spacy
from rdflib.term import Literal
from utilities.wordnet_utility_functions import check_synonymy
from nltk.corpus import wordnet
import re

nlp_analyzer = spacy.load('en_core_web_sm')


def pad_prefix(el, graph):
    return "{:<50}".format(el.n3(graph.namespace_manager))


def prefix(el, graph):
    return pad_prefix(el, graph).strip()


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
# (i.e they are connected with the same predicate, have the same lemma and are both individuals or class)
def check_nodes_equivalence(g1, g2, lemmas, node1, p1, node2, p2):
    # check if the two predicates are the same
    if p1 == p2 and p1 != constants.LABEL_PREDICATE:
        lemma1, lemma2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
        is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
        return (((not is_s1_class) and not is_s2_class) and lemma1 and lemma1 == lemma2) or \
               (is_s1_class and is_s2_class and node1 == node2)
    return False


# return True if the 2 nodes from the 2 graphs received in input are considered equivalent
# (i.e they are connected with the same predicate, have the same lemma and are both individuals or class)
def check_nodes_synonymy(g1, g2, lemmas, node1, p1, node2, p2, threshold_similarity=0.7):
    # check if the two predicates are the same
    if p1 == p2 and p1 != constants.LABEL_PREDICATE:
        wordnet_lemmas = set(wordnet.all_lemma_names())
        is_s1_class, is_s2_class = is_class(node1, g1), is_class(node2, g2)
        if (not is_s1_class) and (not is_s2_class):
            word1, word2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
            # check if the words are in the wordnet dictionary
            if word1 in wordnet_lemmas and word2 in wordnet_lemmas:
                return check_synonymy(word1, word2, threshold_similarity)
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


def superclasses(node, g):
    unwanted_superclasses = ['dul:Event', 'owl:Class']

    classes = list(g.objects(node, constants.TYPE_PREDICATE))
    still_classes = classes != []
    while(still_classes):
        before = len(classes)
        to_add = list(g.objects(classes[-1], constants.SUBCLASS_PREDICATE))
        classes = classes + to_add
        after = len(classes)
        if(after == before):
            still_classes = False
        #print([prefix(c, g) for c in classes])
    classes = filter(lambda x: len(list(g.subjects(constants.TYPE_PREDICATE, x))) < 2, classes)
    return list(filter(lambda x: prefix(x,g) not in unwanted_superclasses, classes))
