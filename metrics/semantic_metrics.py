import numpy as np
import rdflib
from rdflib import Graph
from metrics.metrics_utilities import compute_sentences_lengths, print_scores, plot_data, get_valid_ids_test2, \
    aggregate_scores
import matplotlib as mpl
from utilities import constants
from utilities.utility_functions import get_ids_valid_ontologies, get_categories_from_range


def select_classes_with_semantic_type(sentence_graph, comparison_graph, semantic_type_counter):
    # explore english sentence graph
    # get classes subclasses of the defined semantic types
    list_classes_per_type = {}
    for s, o in sentence_graph.subject_objects(constants.SUBCLASS_PREDICATE):
        vocab_resource = str(o)
        if vocab_resource in constants.SEMANTIC_TYPES:
            counter = 0
            query = """
            PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?subclass WHERE {
                ?subclass rdfs:subClassOf* <""" + vocab_resource + """> .
            }"""
            for row in sentence_graph.query(query):
                # print(row[0], " subclass of ", vocab_resource)
                counter += 1
                if vocab_resource not in list_classes_per_type:
                    list_classes_per_type[vocab_resource] = []
                list_classes_per_type[vocab_resource].append(row[0])
            if vocab_resource in semantic_type_counter:
                semantic_type_counter[vocab_resource] += counter
            else:
                semantic_type_counter[vocab_resource] = counter
    return select_intensional_reifications_from_comparison(list_classes_per_type, comparison_graph)


# select triples from comparison_graph where the intensional reifications of the classes are involved
def select_intensional_reifications_from_comparison(list_classes_per_type, comparison_graph):
    subgraphs = {}
    for semantic_type in list_classes_per_type:
        subgraphs[semantic_type] = Graph()
        subgraph = Graph()
        for class_node in list_classes_per_type[semantic_type]:
            intensional_reifications = comparison_graph.subjects(predicate=constants.SEE_ALSO_PREDICATE, object=class_node)
            for int_reif in intensional_reifications:
                for p, o in comparison_graph.predicate_objects(subject = int_reif):
                    subgraph.add((int_reif, p, o))
                for s, p in comparison_graph.subject_predicates(object = int_reif):
                    subgraph.add((s, p, int_reif))
        subgraphs[semantic_type] += subgraph
    return subgraphs

# {?s tc:onlyIn translation_coherence:""" + en_ontology_name + """}
# UNION {?s tc:synonymy ?o}
def semantic_metric(graph, en_ontology_name=None):
    # {?s tc:stronglyEquivalent ?o} UNION
    # {?s tc:equivalent ?o} UNION
    query = """
        PREFIX translation_coherence:<https://w3id.org/stlab/ke/amiala/>
        PREFIX tc:<https://w3id.org/stlab/ke/amiala/translation_coherence/>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(*) as ?Triples)
        WHERE{
        {?s tc:synonymy ?o}
        ?s ?p ?o .
        }"""
    qres = graph.query(query)
    for row in qres:
        num_triples = int(row["Triples"])
    query = """
        PREFIX translation_coherence: <https://w3id.org/stlab/ke/amiala/>
        PREFIX tc:<https://w3id.org/stlab/ke/amiala/translation_coherence/>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(*) as ?Nodes)
        WHERE{
        {?s tc:equivalent ?o} UNION
        {?s tc:synonymy ?o} UNION
        {?s tc:different ?o} UNION
        {?s tc:differentContext ?o} UNION
        {?s tc:onlyIn ?o}
        ?s ?p ?o .
        }"""
    qres = graph.query(query)
    for row in qres:
        num_nodes = int(row["Nodes"])
    # print("Sentence", str(sentence_id))
    # print("Number of triples: ", str(num_triples))
    # print("Number of nodes: ", str(num_nodes))
    return num_triples / num_nodes


dataset_choice = {"europarl": True, "wikiner": False}

europarl_en_sentences_path = "../Datasets/EuroParl/texts/second_test/first_700_sentences_europarl_en.txt"
wikiner_en_sentences_path = "../Datasets/WikiNER/texts/first_800_sentences_wikiner_en.txt"

europarl_ontologies_path = "../Datasets/EuroParl/ontologies/second_test/"
wikiner_ontologies_path = "../Datasets/WikiNER/ontologies/"
datasets_ontologies_paths = {"europarl": europarl_ontologies_path, "wikiner": wikiner_ontologies_path}

valid_ids_for_lengths = get_valid_ids_test2(dataset_choice["europarl"], dataset_choice["wikiner"], True)
valid_ids = get_valid_ids_test2(dataset_choice["europarl"], dataset_choice["wikiner"], False)

languages_name_mapping = {"de": "German", "it": "Italian", "zh": "Chinese", "fi": "Finnish", "nl": "Dutch",
                          "ko": "Korean"}

if dataset_choice["europarl"] and dataset_choice["wikiner"]:
    lengths = compute_sentences_lengths([europarl_en_sentences_path, wikiner_en_sentences_path], valid_ids_for_lengths)
elif dataset_choice["europarl"]:
    lengths = compute_sentences_lengths([europarl_en_sentences_path], valid_ids_for_lengths)
elif dataset_choice["wikiner"]:
    lengths = compute_sentences_lengths([wikiner_en_sentences_path], valid_ids_for_lengths)

# Compute scores per sentence
semantic_scores = {}
for language in languages_name_mapping.keys():
    semantic_scores[language] = []

for dataset,ontologies_path in datasets_ontologies_paths.items():
    if dataset_choice[dataset]:
        en_sentences_path = ontologies_path + "sentences/"
        comparisons_path = ontologies_path + "comparisons/"
        for language in languages_name_mapping.keys():
            num_triples = 0
            for sentence_id in valid_ids[dataset]:
                en_ontology_name = "en_sentence" + str(sentence_id) + ".ttl"
                ontology_filename = "en_VS_" + language + "_sentence" + str(sentence_id) + ".ttl"
                graph = Graph().parse(comparisons_path + ontology_filename, format="turtle")
                # Select only triples relative to semantic types
                score = semantic_metric(graph, en_ontology_name)
                semantic_scores[language].append(score)
            # print("Language ", language, " num triples: ", num_triples)

# Aggregate and print scores
aggregated_semantic_scores, groups, groups_sizes = aggregate_scores(semantic_scores, lengths)
print_scores(aggregated_semantic_scores, "Equivalent/synonymy scores", groups, groups_sizes, semantic_scores)

# ------------------------------------------
# SEMANTIC ANALYSIS THROUGH TYPES
# ------------------------------------------
# Compute scores per semantic type
# semantic_scores = {}
# graphs_per_semantic_type = {}
# for semantic_type in constants.SEMANTIC_TYPES:
#     graphs_per_semantic_type[semantic_type] = Graph()
#
# semantic_type_counter = {}
#
# # avoided_sentences = {"europarl": [4, 12, 46, 109, 125, 131, 144, 237, 243, 245, 251, 277, 348, 438, 460], "wikiner": []}
#
# for language in languages_name_mapping.keys():
#     semantic_scores[language] = {}
#     for dataset, ontologies_path in datasets_ontologies_paths.items():
#         i = 0
#         if dataset_choice[dataset]:
#             en_sentences_path = ontologies_path + "sentences/"
#             comparisons_path = ontologies_path + "comparisons/"
#             num_triples = 0
#             for sentence_id in valid_ids[dataset]:
#                 # if sentence_id not in avoided_sentences[dataset]:
#                 try:
#                     en_ontology_name = "en_sentence" + str(sentence_id) + ".ttl"
#                     ontology_filename = "en_VS_" + language + "_sentence" + str(sentence_id) + ".ttl"
#                     en_sentence_graph = Graph().parse(en_sentences_path + en_ontology_name, format="turtle")
#                     comparison_graph = Graph().parse(comparisons_path + ontology_filename, format="turtle")
#                     # Select only triples relative to semantic types
#                     comparison_graphs_per_type = select_classes_with_semantic_type(en_sentence_graph, comparison_graph, semantic_type_counter)
#                     # if sentence_id <= 6:
#                         # print("Graph number ", sentence_id)
#                         # print(comparison_graphs_per_type)
#                     # print(comparison_graphs_per_type.keys())
#                     for semantic_type in comparison_graphs_per_type.keys():
#                         semantic_t = str(semantic_type)
#                         # print(semantic_t)
#                         graphs_per_semantic_type[semantic_t] += comparison_graphs_per_type[semantic_t]
#                     i += 1
#                 except:
#                     pass
#
#     for semantic_type in graphs_per_semantic_type.keys():
#         semantic_t = str(semantic_type)
#         score = semantic_metric(graphs_per_semantic_type[semantic_t])
#         # print(semantic_t)
#         semantic_scores[language][semantic_t] = score
#
# aggregated_semantic_scores = semantic_scores
# print_scores(aggregated_semantic_scores, "Equivalent/synonymy scores", constants.SEMANTIC_TYPES, None, None)

# ------------------------------------------
# PLOTTING
# ------------------------------------------

y = []
y_data_label = []
for language, scores_by_group in aggregated_semantic_scores.items():
    y.append([np.mean(scores) for scores in scores_by_group])
    # y.append([scores for scores in scores_by_group.values()])
    y_data_label.append(languages_name_mapping[language])

x = get_categories_from_range(lengths, groups)

# Choose the graph settings based on the metric
# Equivalent
# plot_data(x, mpl.pyplot.plot, y, y_data_label,
#           "Elements of the english sentence's graph for which there is an equivalent correspondence",
#           "Sentences' lengths", "Equivalent elements", False)
# Equivalent/Synonymy
# plot_data(x, mpl.pyplot.plot, y, y_data_label,
#           "Elements of the english sentence's graph for which there is an equivalent/synonymy correspondence",
#           "Sentences' lengths", "Equivalent/synonym elements", False)
# Synonymy
plot_data(x, mpl.pyplot.plot, y, y_data_label,
          "Elements of the english sentence's graph for which there is an synonym correspondence",
          "Sentences' lengths", "Synonym elements", False)
# Different
# plot_data(x, mpl.pyplot.plot, y, y_data_label,
#           "Elements of the english sentence's graph for which there is a 'different' correspondence",
#           "Sentences' lengths", "Different elements", False)
# OnlyIn
# plot_data(x, mpl.pyplot.plot, y, y_data_label,
#           "Elements of the english sentence's graph for which there is no correspondence",
#           "Sentences' lengths", "Only in English sentence elements", False)
# DifferentContext
# plot_data(groups, mpl.pyplot.plot, y, y_data_label,
#           "Elements of the english sentence's graph for which are in a different context",
#           "Sentences' lengths", "Different context English sentence elements", False)

# x = [x.split("#")[-1] for x in constants.SEMANTIC_TYPES]
#
# # Semantic Types
# plot_data(x, mpl.pyplot.plot, y, y_data_label,
#           "Classes of the english sentence's graph equivalent", "Semantic types",
#           "Equivalent elements", False)

# Different error analysis
        # query = """
        #     PREFIX translation_coherence:<https://w3id.org/stlab/ke/amiala/>
        #     PREFIX tc:<https://w3id.org/stlab/ke/amiala/translation_coherence/>
        #     PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        #     SELECT *
        #     WHERE{
        #     {?s tc:different ?o}
        #     }"""
        # qres = graph.query(query)
        # for row in qres:
        #     print(row)