from nltk.corpus import wordnet
from nltk.corpus.reader import WordNetError

# nltk.download("wordnet")


# return all the synonyms of all the possible meanings of word (return a list of strings)
def get_word_synonyms(word):
    return [str(lemma.name()) for syn_set in wordnet.synsets(word) for lemma in syn_set.lemmas()]


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


# return True if two words are synonyms according to some rules that rely on Wordnet synsets and similarity metrics
def check_synonymy(word1, word2, threshold_similarity):
    if word1 in get_word_synonyms(word2):
        return True
    # otherwise compute the max similarity between all possible synsest (using path and wup similarity)
    similarity = 0
    # for each pair of synset compute the similarity and find the maximum
    for synset1, synset2 in zip(wordnet.synsets(word1), wordnet.synsets(word2)):
        new_similarity = 0.33 * synset1.path_similarity(synset2) + 0.67 * synset1.wup_similarity(synset2)
        similarity = max(similarity, new_similarity) if word1 and word2 else 0
    # the two words are synonyms if the similarity is above a certain threshold
    return similarity >= threshold_similarity
