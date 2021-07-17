from scipy import spatial
import numpy as np
import re
import constants
from utility_functions import prefix, lemma, word, get_word_synonyms, extract_synset
from nltk.corpus import wordnet, wordnet_ic


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


# find the pairs of synonyms in the 2 graphs
def find_synonyms(g1, g2, lemmas, n, result_graph):
    synonyms = set()
    # extract the set of IRI and their corresponding word from the graphs
    for node1 in g1.all_nodes():
        word1 = str(g1.label(node1))
        lemma1 = lemmas[word1]
        for node2 in g2.all_nodes():
            word2 = str(g2.label(node2))
            lemma2 = lemmas[word2]
            word1_synonyms = get_word_synonyms(lemma1)
            # if the 2 words are different and they are synonyms
            if lemma1 != lemma2 and lemma2 in word1_synonyms:
                new_synonyms_pair = (word1, word2) if word1 < word2 else (word2, word1)
                synonyms.add(new_synonyms_pair)
                result_graph.add((node1, n.similar_to, node2))
    return synonyms


# find the pairs of synonyms in the 2 graphs
# similarity_function indicate the wordnet metric for similarity between (path, lch, wup)
# max_or_average indicates if either the average or the maximum of all the similarities between the synsets of the words
# should be greater than the threshold
def find_similar_words(g1, g2, lemmas, n, result_graph, similarity_function, threshold, max_or_average="max"):
    synonyms = set()
    # exploring the graph
    for node1 in g1.all_nodes():
        word1 = str(g1.label(node1))
        lemma1 = lemmas[word1]
        for node2 in g2.all_nodes():
            word2 = str(g2.label(node2))
            lemma2 = lemmas[word2]
            synonymy = False
            similarity_sum = 0
            n_comparisons = 0
            for synset1 in wordnet.synsets(lemma1):
                for synset2 in wordnet.synsets(lemma2):
                    n_comparisons += 1
                    if synset1.pos() != synset2.pos():
                        similarity = 0
                    elif similarity_function == "combination":
                        similarity = 0.33 * synset1.path_similarity(synset2) + 0.67 * synset1.wup_similarity(synset2)
                    elif similarity_function == "path":
                        similarity = synset1.path_similarity(synset2)
                    elif similarity_function == "lch":
                        similarity = 0 if synset1.pos != synset2.pos else synset1.lch_similarity(synset2)
                    elif similarity_function == "wup":
                        similarity = synset1.wup_similarity(synset2)
                    # They don't work
                    # elif similarity_function == "res":
                    #     similarity = synset1.res_similarity(synset2, wordnet_ic.ic())
                    # elif similarity_function == "jcn":
                    #     similarity = synset1.jcn_similarity(synset2, wordnet_ic.ic())
                    # elif similarity_function == "lin":
                    #     similarity = synset1.lis_similarity(synset2, wordnet_ic.ic())
                    # if the 2 words are different and they are synonyms
                    similarity_sum += similarity
                    if max_or_average == "max" and lemma1 != lemma2 and similarity > threshold:
                         synonymy = True
            similarity = 0 if not n_comparisons else similarity_sum / n_comparisons
            if max_or_average == "average" and lemma1 != lemma2 and similarity > threshold:
                synonymy = True
            if synonymy:
                new_synonyms_pair = (word1, word2) if word1 < word2 else (word2, word1)
                synonyms.add(new_synonyms_pair)
    return synonyms


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
