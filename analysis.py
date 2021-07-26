from scipy import spatial
import numpy as np
from utilities.utility_functions import extract_words
from utilities.wordnet_utility_functions import extract_synset, get_word_synonyms
from nltk.corpus import wordnet


# find the pairs of synonyms in the 2 graphs
def find_synonyms(g1, g2, lemmas):
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
    return synonyms


# find the pairs of synonyms in the 2 graphs
# similarity_function indicate the wordnet metric for similarity between (path, lch, wup)
# max_or_average indicates if either the average or the maximum of all the similarities between the synsets of the words
# should be greater than the threshold
def find_similar_words(g1, g2, lemmas, similarity_function, threshold, max_or_average="max"):
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
                    if max_or_average == "max" and lemma1 != lemma2 and similarity >= threshold:
                         synonymy = True
            similarity = 0 if not n_comparisons else similarity_sum / n_comparisons
            if max_or_average == "average" and lemma1 != lemma2 and similarity >= threshold:
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
