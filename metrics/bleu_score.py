import numpy as np
from metrics_utilities import compute_bleu_score, aggregate_scores, print_scores, compute_sentences_lengths, plot_data, \
    get_valid_ids_test2, compute_meteor_score
from utilities.utility_functions import get_ids_valid_ontologies, get_categories_from_range
import matplotlib as mpl

EuroParl = True
WikiNER = False

europarl_en_sentences_path = "../Datasets/EuroParl/texts/second_test/first_700_sentences_europarl_en.txt"
wikiner_en_sentences_path = "../Datasets/WikiNER/texts/first_800_sentences_wikiner_en.txt"

languages_name_mapping = {"de": "German", "it": "Italian", "zh": "Chinese", "fi": "Finnish", "nl": "Dutch", "ko": "Korean"}

original_texts = []
if EuroParl:
    input_file = open(europarl_en_sentences_path, "r")
    original_texts += [[line.rstrip('\n').split(" ")] for line in input_file.readlines()]
    input_file.close()
if WikiNER:
    input_file = open(wikiner_en_sentences_path, "r")
    original_texts += [[line.rstrip('\n').split(" ")] for line in input_file.readlines()]
    input_file.close()
texts_variations = dict()

for language in languages_name_mapping.keys():
    texts_variations[language] = []
    if EuroParl:
        input_file = open("../Datasets/EuroParl/texts/second_test/first_700_sentences_europarl_" + language + ".txt", "r")
        texts_variations[language] += [line.rstrip('\n').split(" ") for line in input_file.readlines()]
        input_file.close()
    if WikiNER:
        input_file = open("../Datasets/WikiNER/texts/first_800_sentences_wikiner_" + language + ".txt", "r")
        texts_variations[language] += [line.rstrip('\n').split(" ") for line in input_file.readlines()]
        input_file.close()

valid_ids = get_valid_ids_test2(EuroParl, WikiNER, True)

# folders = ["../EuroParl/ontologies/first_test/comparisons/"]
# valid_ids = get_ids_valid_ontologies(folders)
# valid_ids = list(range(1, 200))

bleu_scores = {}

if EuroParl and WikiNER:
    lengths = compute_sentences_lengths([europarl_en_sentences_path, wikiner_en_sentences_path], valid_ids)
elif EuroParl:
    lengths = compute_sentences_lengths([europarl_en_sentences_path], valid_ids)
elif WikiNER:
    lengths = compute_sentences_lengths([wikiner_en_sentences_path], valid_ids)
bleu_scores = compute_bleu_score(original_texts, texts_variations, valid_ids)
aggregated_bleu_scores, groups, groups_sizes = aggregate_scores(bleu_scores, lengths)
# print(aggregated_bleu_scores)
print_scores(aggregated_bleu_scores, "BLEU scores", groups, groups_sizes, bleu_scores)

y = []
y_data_label = []
for k, v in aggregated_bleu_scores.items():
    y.append([np.mean(group) for group in v])
    y_data_label.append(languages_name_mapping[k])

length_range = get_categories_from_range(lengths, groups)
plot_data(length_range, mpl.pyplot.bar, [groups_sizes], ["Groups dimensions"], "Group of sentences",
          "Sentences' lengths", "Number of sentences", True)

plot_data(length_range, mpl.pyplot.plot, y, y_data_label, "METEOR scores", "Sentences' lengths", "METEOR score", True)