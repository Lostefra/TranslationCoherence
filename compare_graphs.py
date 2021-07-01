from rdflib import Namespace, Graph
from build_graph import graph_bind
from nltk.corpus import wordnet
from nltk.corpus.reader import WordNetError
from scipy import spatial
import numpy as np
import re

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

#return all the synonyms of all the possible meanings of word (return a list of strings) 
def get_word_synonyms(word):
    return [str(lemma.name()) for syn_set in wordnet.synsets(word) for lemma in syn_set.lemmas()]

#find the pairs of synonyms in the 2 graphs
def find_synonyms(g2, g1, n, result_graph):
    #extract the set of IRI and their corresponding word from the graphs
    g1_words = extract_words(g1)
    g2_words = extract_words(g2)
    #for each pair of words, check if they are synonyms
    for iri1, word1 in g1_words:
        g1_synonyms = get_word_synonyms(word1)
        for iri2, word2 in g2_words:
            # if the 2 words are different and they are synonyms
            lemma2 = lemmatizer.lemmatize(word2)
            if word1 != word2 and lemma2 in g1_synonyms:
                print(word1, word2)
                #g2_synonyms = get_word_synonyms(word2)
                #print(word1, "has synonyms ", g1_synonyms)
                #print(word2, "has synonyms ", g2_synonyms)
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


def compare_graphs(g1, g2):
    n = Namespace("http://example.org/translation_coherence/")
    result_graph = Graph()
    indexes = {}
    for name in ["expressions"]:
        indexes[name] = index_generator()

    # Populate result_graph by recognizing patterns on g1, g2
    sameAs_equivalentClass_transitivity(g1, g2, n, result_graph)
    negative_verbs(g1, g2, n, result_graph, indexes)
    negative_verbs(g2, g1, n, result_graph, indexes)
    print("WordNet (synset)")
    find_synonyms(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("WordNet (wup_similarity)")
    synonyms1(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################
    print("GloVe")
    synonyms2(g1, g2, n, result_graph)
    print("-" * 150)  # #########################################################

    graph_bind(result_graph)
    return result_graph
