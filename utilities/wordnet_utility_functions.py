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
def check_synonymy(word1, word2, threshold_wup_similarity=0.85, threshold_path_similarity=0.45):
    if word1 in get_word_synonyms(word2):
        return True
    # otherwise compute the max similarity between all possible synsest (using path and wup similarity)
    wup_similarity = 0
    path_similarity = 0
    # for each pair of synset compute the similarity and find the maximum
    for synset1 in wordnet.synsets(word1):
        for synset2 in wordnet.synsets(word2):
            if word1 and word2:
                new_path_similarity = synset1.path_similarity(synset2)
                path_similarity = max(path_similarity, new_path_similarity)
                new_wup_similarity = synset1.wup_similarity(synset2)
                wup_similarity = max(wup_similarity, new_wup_similarity)
                # new_combined_similarity = 0.33 * path_similarity + 0.67 * wup_similarity
                # combined_similarity = max(similarity, new_combined_similarity)
    # the two words are synonyms if the similarity is above a certain threshold
    return path_similarity >= threshold_path_similarity or wup_similarity >= threshold_wup_similarity

