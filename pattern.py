from nltk.corpus import wordnet
from nltk.corpus.reader import WordNetError
from scipy import spatial
import numpy as np
import re
import constants
from utility_functions import prefix, lemma, word


def negative_verbs(g1, g2, n, result_graph, indexes):
    # Identify verbs which give a negative meaning to the expressions
    for s1, p1, o1 in g1:
        if "fred:fail" in prefix(s1, g1) and prefix(p1, g1) == "vn.role:Theme":
            for s2, p2, o2 in g2:
                if prefix(o1, g1) == prefix(s2, g2) and prefix(p2, g2) == "boxing:hasTruthValue" and prefix(o2, g2) == "boxing:False":
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


# find the pairs of synonyms in the 2 graphs
def find_synonyms(g2, g1, n, result_graph):
    # extract the set of IRI and their corresponding word from the graphs
    g1_words = extract_words(g1)
    g2_words = extract_words(g2)
    # for each pair of words, check if they are synonyms
    for iri1, word1 in g1_words:
        lemma1 = lemma(word1)
        g1_synonyms = get_word_synonyms(lemma1)
        for iri2, word2 in g2_words:
            # if the 2 words are different and they are synonyms
            lemma2 = lemma(word2)
            if lemma1 != lemma2 and lemma2 in g1_synonyms:
                # print(word1, word2)
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
                # print(word1, word2, similarity)
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
                # print(word1, word2, similarity)
                if similarity > 0.8:
                    result_graph.add((iri1, n.similar_to, iri2))


def dbpedia_equivalence(g1, g2, n, result_graph):
    # Check if a dbpedia object appears in both ontologies, in one case as an individual and in the other as a class.
    # In this case, add the triple (s, sameAs, o), where s is the fred object in a "owl:sameAs" relation with the dbpedia individual,
    # and o is the instance of the fred object in a "owl:equivalentClass" relation with the dbpedia class (or viceversa).

    # Store pairs of objects to relate
    # In the first list the order is g1,g2; in the second list the order is g2,g1
    # (only useful to print)
    to_match = [[], []]
    for s1, p1, o1 in g1:
        if prefix(p1, g1) == "owl:equivalentClass":
            # Check same object in a "owl:sameAs" relation
            for s2, p2, o2 in g2:
                if any(["dbpedia" in i for i in [prefix(s1, g1), prefix(s2, g2), prefix(o1, g1), prefix(o2, g2)]]):
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: o2, instance of o1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], o2))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: o2, instance of s1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], o2))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: s2, instance of o1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], s2))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: s2, instance of s1
                        to_match[0].append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], s2))

        elif prefix(p1, g1) == "owl:sameAs":
            # Check same object in a "owl:equivalentClass" relation
            for s2, p2, o2 in g2:
                if any(["dbpedia" in i for i in [prefix(s1, g1), prefix(s2, g2), prefix(o1, g1), prefix(o2, g2)]]):
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: o1, instance of o2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0], o1))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: s1, instance of o2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0], s1))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: o1, instance of s2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0], o1))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: s1, instance of s2
                        to_match[1].append(([i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0], s1))

    # Add matches found to result graph
    # Pairs g1,g2
    for s, o in to_match[0]:
        # print(prefix(s,g1), "owl:sameAs", prefix(o,g2))
        result_graph.add((s, constants.SAME_AS_PREDICATE, o))
    # Pairs g2,g1
    for s, o in to_match[1]:
        # print(prefix(s,g2), "owl:sameAs", prefix(o,g1))
        result_graph.add((s, constants.SAME_AS_PREDICATE, o))
