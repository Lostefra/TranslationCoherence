from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pymeteor.pymeteor as pymeteor
from utilities.utility_functions import get_ids_valid_ontologies


def compute_group_index(n, separators):
    for i in range(len(separators)):
        if n <= separators[i]:
            return i
    return i


def compute_machine_translation_score(machine_translation_metric, original_texts, texts_variations, valid_ids):
    scores = {}
    for language in texts_variations.keys():
        scores[language] = []
        for i, sentence_id in enumerate(valid_ids):
            score = machine_translation_metric(original_texts[sentence_id - 1], texts_variations[language][sentence_id - 1])
            scores[language].append(score)
    return scores


def compute_bleu_score(original_texts, texts_variations, valid_ids):
    return compute_machine_translation_score(sentence_bleu, original_texts, texts_variations, valid_ids)


def compute_meteor_score(original_texts, texts_variations, valid_ids):
    original_texts = [str.join(" ", text[0]) for text in original_texts]
    for key in texts_variations.keys():
        texts_variations[key] = [str.join(" ", text) for text in texts_variations[key]]
    return compute_machine_translation_score(pymeteor.meteor, original_texts, texts_variations, valid_ids)


def aggregate_scores(scores, lengths):
    # divido le frasi in 8 gruppi secondo la loro lunghezza
    groups = [int(np.percentile(sorted(lengths), p/10)) for p in range(125, 1100, 125)]
    # groups = [7, 11, 14, 18, 24, 28, 40, 105]
    groups_sizes = []

    previous_group = 0
    for q in groups:
        current_group_size = sum([1 if length <= q else 0 for length in lengths]) - previous_group
        groups_sizes.append(current_group_size)
        previous_group += current_group_size

    aggregated_scores = {}

    for language in scores.keys():
        aggregated_scores[language] = []
        for i, length in enumerate(lengths):
            # print(str(length), " => ", str(index))
            index = compute_group_index(length, groups)
            while index > len(aggregated_scores[language]) - 1:
                aggregated_scores[language].append([])
            aggregated_scores[language][index].append(scores[language][i])
    return aggregated_scores, groups, groups_sizes


def compute_sentences_lengths(sentences_filenames, valid_ids):
    original_texts = []
    for sentences_filename in sentences_filenames:
        input_file = open(sentences_filename, "r")
        original_texts += [[line.rstrip('\n').split(" ")] for line in input_file.readlines()]
        input_file.close()
    lengths = []
    for sentence_id in valid_ids:
        length = len(original_texts[sentence_id - 1][0])
        lengths.append(length)
    return lengths


def print_scores(aggregated_scores, title, groups, groups_sizes = None, scores_by_sentence = None):
    print(title)
    if scores_by_sentence != None:
        for language in scores_by_sentence.keys():
            print(language, "average: {:.3f}".format(np.mean(scores_by_sentence[language])))
            print(language, "variance: {:.4f}".format(np.var(scores_by_sentence[language])))

    for language in aggregated_scores.keys():
        print("Language: ", language)
        for i in range(len(groups)):
            if isinstance(aggregated_scores[language], list):
                print("Set of sentences until {}: {:.3f} (variance {:.4f})".format(
                    groups[i], np.mean(aggregated_scores[language][i]), np.var(aggregated_scores[language][i])))
            else:
                print("Set of sentences until {}: {:.3f} (variance {:.4f})".format(
                    groups[i], np.mean(aggregated_scores[language][groups[i]]), np.var(aggregated_scores[language][groups[i]])))
    if groups_sizes != None:
        print("Groups: ", groups, " with sizes ", groups_sizes)


# y and data_label should be list of the same dimension
def plot_data(x, plotting_function, y, data_label, title, x_label, y_label, integer):
    # Note that even in the OO-style, we use `.pyplot.figure` to create the figure.
    fig, ax = plt.subplots()  # Create a figure and an axes.
    for i, data in enumerate(y):
        plotting_function(x, data, label=data_label[i])  # Plot some data on the axes.
    ax.set_xlabel(x_label)  # Add an x-label to the axes.
    ax.set_ylabel(y_label)  # Add a y-label to the axes.
    if integer:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.ylim((ylim[0], ylim[1]))
    ax.set_title(title)  # Add a title to the axes.
    ax.legend()  # Add a legend.
    plt.show()


def get_valid_ids_test2(EuroParl, WikiNER, serialize):
    dataset_paths = {"europarl": "../Datasets/EuroParl/ontologies/second_test/", "wikiner": "../Datasets/WikiNER/ontologies/"}
    valid_ids = {}
    for dataset, dataset_path in dataset_paths.items():
        if (dataset == "europarl" and EuroParl) or (dataset == "wikiner" and WikiNER):
            folders = [dataset_path + "en/", dataset_path + "de/",
                       dataset_path + "it/", dataset_path + "zh/",
                       dataset_path + "fi/", dataset_path + "nl/",
                       dataset_path + "ko/"]
            valid_ids[dataset] = get_ids_valid_ontologies(folders)
            if dataset == "wikiner":
                # WikiNER sentences broken
                # DE
                valid_ids[dataset].remove(101)
                valid_ids[dataset].remove(116)
                valid_ids[dataset].remove(155)
                valid_ids[dataset].remove(180)
                valid_ids[dataset].remove(225)
                valid_ids[dataset].remove(349)
                valid_ids[dataset].remove(405)
                valid_ids[dataset].remove(432)
                valid_ids[dataset].remove(483)
                valid_ids[dataset].remove(564)
                valid_ids[dataset].remove(641)
                valid_ids[dataset].remove(678)
                valid_ids[dataset].remove(734)
                valid_ids[dataset].remove(744)
                # IT
                valid_ids[dataset].remove(40)
                valid_ids[dataset].remove(55)
                valid_ids[dataset].remove(210)
                valid_ids[dataset].remove(232)
                valid_ids[dataset].remove(274)
                valid_ids[dataset].remove(304)
                valid_ids[dataset].remove(342)
                valid_ids[dataset].remove(414)
                valid_ids[dataset].remove(630)
                valid_ids[dataset].remove(670)
                valid_ids[dataset].remove(711)
                valid_ids[dataset].remove(745)
                # ZH
                valid_ids[dataset].remove(102)
                valid_ids[dataset].remove(103)
                # FI
                valid_ids[dataset].remove(104)
                valid_ids[dataset].remove(125)
                valid_ids[dataset].remove(290)
                valid_ids[dataset].remove(511)
                valid_ids[dataset].remove(777)
                # NL
                valid_ids[dataset].remove(41)
                valid_ids[dataset].remove(212)
                valid_ids[dataset].remove(339)
                valid_ids[dataset].remove(355)
                valid_ids[dataset].remove(537)
                valid_ids[dataset].remove(547)
                valid_ids[dataset].remove(760)
                valid_ids[dataset].remove(762)
                # KO
                valid_ids[dataset].remove(48)
                valid_ids[dataset].remove(109)
                valid_ids[dataset].remove(132)
                valid_ids[dataset].remove(149)
                valid_ids[dataset].remove(181)
                valid_ids[dataset].remove(252)
                valid_ids[dataset].remove(410)
                valid_ids[dataset].remove(543)
                valid_ids[dataset].remove(574)
                valid_ids[dataset].remove(668)
                valid_ids[dataset].remove(800)
                # Comparison
                valid_ids[dataset].remove(93)
                valid_ids[dataset].remove(131)
                valid_ids[dataset].remove(167)
                valid_ids[dataset].remove(170)
                valid_ids[dataset].remove(171)
                valid_ids[dataset].remove(193)
                valid_ids[dataset].remove(289)
                valid_ids[dataset].remove(430)
                valid_ids[dataset].remove(457)
                valid_ids[dataset].remove(579)
                valid_ids[dataset].remove(597)
                    # IT
                valid_ids[dataset].remove(20)
                valid_ids[dataset].remove(21)
                valid_ids[dataset].remove(38)
                valid_ids[dataset].remove(47)
                valid_ids[dataset].remove(86)
                valid_ids[dataset].remove(151)
                valid_ids[dataset].remove(320)
                valid_ids[dataset].remove(321)
                valid_ids[dataset].remove(322)
                valid_ids[dataset].remove(428)
                valid_ids[dataset].remove(458)
                valid_ids[dataset].remove(531)
                    # ZH
                valid_ids[dataset].remove(119)
                valid_ids[dataset].remove(166)
                valid_ids[dataset].remove(359)
                valid_ids[dataset].remove(416)
                    # FI
                valid_ids[dataset].remove(108)
                valid_ids[dataset].remove(147)
                valid_ids[dataset].remove(251)
                valid_ids[dataset].remove(714)
                    # NL
                valid_ids[dataset].remove(177)
            if dataset == "europarl":
                # EuroParl sentences broken
                # EN/DE
                valid_ids[dataset].remove(9)
                valid_ids[dataset].remove(18)
                valid_ids[dataset].remove(195)
                valid_ids[dataset].remove(242)
                valid_ids[dataset].remove(333)
                valid_ids[dataset].remove(463)
                valid_ids[dataset].remove(532)
                valid_ids[dataset].remove(594)
                valid_ids[dataset].remove(631)
                # IT
                valid_ids[dataset].remove(403)
                # ZH
                valid_ids[dataset].remove(57)
                valid_ids[dataset].remove(226)
                # FI
                valid_ids[dataset].remove(462)
                valid_ids[dataset].remove(573)
                # NL
                valid_ids[dataset].remove(662)
                # KO
                valid_ids[dataset].remove(53)
                valid_ids[dataset].remove(358)
                valid_ids[dataset].remove(381) # exceeded quota
                valid_ids[dataset].remove(391) # exceeded quota
                valid_ids[dataset].remove(668)
                # Comparison
                valid_ids[dataset].remove(197)
                valid_ids[dataset].remove(232)
                valid_ids[dataset].remove(236)
                valid_ids[dataset].remove(288)
                valid_ids[dataset].remove(314)
                valid_ids[dataset].remove(371)
                valid_ids[dataset].remove(35)
                valid_ids[dataset].remove(352)
                valid_ids[dataset].remove(534)
                valid_ids[dataset].remove(659)
                valid_ids[dataset].remove(74)
                valid_ids[dataset].remove(99)
                valid_ids[dataset].remove(116)
                valid_ids[dataset].remove(397)
                valid_ids[dataset].remove(401)
                valid_ids[dataset].remove(121)
                valid_ids[dataset].remove(123)
                valid_ids[dataset].remove(1)
                valid_ids[dataset].remove(292)
                valid_ids[dataset].remove(313)
                valid_ids[dataset].remove(553)
                valid_ids[dataset].remove(700)
    # print("EuroParl size: ", len(valid_ids["europarl"]))
    # print("WikiNER size: ", len(valid_ids["wikiner"]))
    if serialize:
        if EuroParl and WikiNER:
            valid_ids = [id if k == "europarl" else id + 700 for k, ids in valid_ids.items() for id in ids]
        elif EuroParl and not WikiNER:
            valid_ids = valid_ids["europarl"]
        elif WikiNER and not EuroParl:
            valid_ids = valid_ids["wikiner"]
    return valid_ids