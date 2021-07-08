from rdflib import Namespace, Graph, term
from build_graph import graph_bind
from nltk.corpus import wordnet
from nltk.corpus.reader import WordNetError
from scipy import spatial
import numpy as np
import re
import constants

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


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
    return result_graph


def negative_verbs(g1, g2, n, result_graph, indexes):
    # Identify verbs which give a negative meaning to the expressions
    for s1, p1, o1 in g1:
        if "fred:fail" in prefix(s1, g1) and prefix(p1, g1) == "vn.role:Theme":
            for s2, p2, o2 in g2:
                if prefix(o1, g1) == prefix(s2, g2) and prefix(p2, g2) == "boxer:hasTruthValue" and prefix(o2, g2) == "boxer:False":
                    # "Expression_i" is a reification of a N-ary relationship
                    expr1 = "expression_" + next(indexes["expressions"])
                    expr2 = "expression_" + next(indexes["expressions"])

                    result_graph.add((n[expr1], n.involves_aux, s1))
                    result_graph.add((n[expr1], n.involves_verb, o1))

                    result_graph.add((n[expr2], p2, o2))
                    result_graph.add((n[expr2], n.involves_verb, s2))

                    result_graph.add((n[expr1], n.same_expression, n[expr2]))


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


def extract_synset(w):
    # Hypothesis: only the first sense is taken
    try:
        return wordnet.synset(w + ".n.01")  # noun
    except WordNetError:
        try:
            return wordnet.synset(w + ".v.01")  # verb
        except WordNetError:
            try:
                return wordnet.synset(w + ".a.01")  # adjective
            except WordNetError:
                try:
                    return wordnet.synset(w + ".r.01")  # adverb
                except WordNetError:
                    try:
                        return wordnet.synset(w + ".s.01")  # adjective satellite
                    except WordNetError:
                        return None


# return all the synonyms of all the possible meanings of word (return a list of strings)
def get_word_synonyms(word):
    return [str(lemma.name()) for syn_set in wordnet.synsets(word) for lemma in syn_set.lemmas()]


# find the pairs of synonyms in the 2 graphs
def find_synonyms(g2, g1, n, result_graph):
    # extract the set of IRI and their corresponding word from the graphs
    g1_words = extract_words(g1)
    g2_words = extract_words(g2)
    # for each pair of words, check if they are synonyms
    for iri1, word1 in g1_words:
        g1_synonyms = get_word_synonyms(word1)
        for iri2, word2 in g2_words:
            # if the 2 words are different and they are synonyms
            lemma2 = lemmatizer.lemmatize(word2)
            if word1 != word2 and lemma2 in g1_synonyms:
                print(word1, word2)
                # g2_synonyms = get_word_synonyms(word2)
                # print(word1, "has synonyms ", g1_synonyms)
                # print(word2, "has synonyms ", g2_synonyms)
                result_graph.add((iri1, n.similar_to, iri2))


def synonyms1(g2, g1, n, result_graph):
    # Check synonyms in graphs using Wordnet
    """
    To use WordNet, first download it:
    >> import nltk
    >> nltk.download("wordnet")
    """
    # Extract the set of IRI and their corresponding word from the graphs
    g1_words = extract_words(g1)
    g2_words = extract_words(g2)
    # Compare pairwise the words computing the cosine similarity
    for iri1, word1 in g1_words:
        synset1 = extract_synset(word1)
        for iri2, word2 in g2_words:
            synset2 = extract_synset(word2)
            # Avoid comparison of the word with itself
            if word1 != word2:
                similarity = synset1.wup_similarity(synset2)
                print(word1, word2, similarity)
                if similarity > 0.8:
                    result_graph.add((iri1, n.similar_to, iri2))


def synonyms2(g2, g1, n, result_graph):
    # Check synonyms in graphs using GloVe
    embeddings_dict = {}
    # Load GloVe word embeddings, download the file from http://nlp.stanford.edu/data/glove.6B.zip (820 Mb)
    with open("glove/glove.6B.50d.txt", 'r', encoding="utf8") as f:
        for line in f:
            values = line.split()
            w = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[w] = vector

    # Extract the set of IRI and their corresponding word from the graphs
    g1_words = extract_words(g1)
    g2_words = extract_words(g2)
    # Compare pairwise the words computing the cosine similarity
    for iri1, word1 in g1_words:
        encoding1 = embeddings_dict[word1]
        for iri2, word2 in g2_words:
            encoding2 = embeddings_dict[word2]
            # Avoid comparison of the word with itself
            if word1 != word2:
                similarity = 1 - spatial.distance.cosine(encoding1, encoding2)
                print(word1, word2, similarity)
                if similarity > 0.8:
                    result_graph.add((iri1, n.similar_to, iri2))

def dbpedia_equivalence(g1, g2, n, result_graph):
    #Check if a dbpedia object appears in both ontologies, in one case as an individual and in the other as a class.
    #In this case, add the triple (s, sameAs, o), where s is the fred object in a "owl:sameAs" relation with the dbpedia individual,
    #and o is the instance of the fred object in a "owl:equivalentClass" relation with the dbpedia class (or viceversa).
    
    #Store pairs of objects to relate
    #In the first list the order is g1,g2; in the second list the order is g2,g1
    #(only useful to print)
    to_match = [[],[]]
    for s1,p1,o1 in g1:
        if prefix(p1, g1) == "owl:equivalentClass":
            #Check same object in a "owl:sameAs" relation
            for s2,p2,o2 in g2:
                if any(["dbpedia" in i for i in [prefix(s1, g1), prefix(s2, g2), prefix(o1, g1), prefix(o2, g2)]]):
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (prefix(p2, g2) == "owl:sameAs"):
                        #To match: o2, instance of o1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], o2))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (prefix(p2, g2) == "owl:sameAs"):
                        #To match: o2, instance of s1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], o2))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (prefix(p2, g2) == "owl:sameAs"):
                        #To match: s2, instance of o1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], s2))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (prefix(p2, g2) == "owl:sameAs"):
                        #To match: s2, instance of s1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], s2))
    
        elif prefix(p1, g1) == "owl:sameAs":
            #Check same object in a "owl:equivalentClass" relation
            for s2,p2,o2 in g2:
                if any(["dbpedia" in i for i in [prefix(s1, g1), prefix(s2, g2), prefix(o1, g1), prefix(o2, g2)]]):
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (prefix(p2, g2) == "owl:equivalentClass"):
                        #To match: o1, instance of o2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0], o1))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (prefix(p2, g2) == "owl:equivalentClass"):
                        #To match: s1, instance of o2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0], s1))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (prefix(p2, g2) == "owl:equivalentClass"):
                        #To match: o1, instance of s2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0], o1))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (prefix(p2, g2) == "owl:equivalentClass"):
                        #To match: s1, instance of s2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0], s1))
    
    #Add matches found to result graph
    #Pairs g1,g2
    for s,o in to_match[0]:
        print(prefix(s,g1), "owl:sameAs", prefix(o,g2))
        result_graph.add((s, constants.SAME_AS_PREDICATE, o))
    #Pairs g2,g1
    for s,o in to_match[1]:
        print(prefix(s,g2), "owl:sameAs", prefix(o,g1))
        result_graph.add((s, constants.SAME_AS_PREDICATE, o))


def compare_graphs(g1, g2):
    n = Namespace("http://example.org/translation_coherence/")
    result_graph = Graph()
    indexes = {}
    for name in ["expressions"]:
        indexes[name] = index_generator()

    # Populate result_graph by recognizing patterns on g1, g2
    #find_equivalence(g1, g2, n, result_graph)
    # negative_verbs(g1, g2, n, result_graph, indexes)
    # negative_verbs(g2, g1, n, result_graph, indexes)
    # print("WordNet (synset)")
    # find_synonyms(g1, g2, n, result_graph)
    # print("-" * 150)  # #########################################################
    # print("WordNet (wup_similarity)")
    # synonyms1(g1, g2, n, result_graph)
    # print("-" * 150)  # #########################################################
    # print("GloVe")
    # synonyms2(g1, g2, n, result_graph)
    # print("-" * 150)  # #########################################################
    print("DBPedia equivalence")
    dbpedia_equivalence(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################

    graph_bind(result_graph)
    return result_graph
