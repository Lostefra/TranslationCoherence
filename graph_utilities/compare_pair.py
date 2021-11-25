from graph_utilities.pattern_utility import apply_intensional_reification
from utilities.utility_functions import pad_prefix
from graph_utilities.build_graph import build_graph
from graph_utilities.compare_graphs import compare_graphs
from graph_utilities.deploy_graph import serialize_graph, update_graph_iri, add_annotations


def compare_pair(lang_1, filename_1, lang_2, filename_2, sentence):
    print("Comparing: " + lang_1 + ", " + lang_2 + " for " + sentence)

    g1 = build_graph(filename_1)
    g2 = build_graph(filename_2)

    # Generate the knowledge graph containing the semantic comparison between g1, g2
    rg = compare_graphs(g1, g2)

    g1, g1_name, g2, g2_name, result_graph, rg_name = update_graph_iri(g1, g2, rg, lang_1, lang_2, sentence)
    apply_intensional_reification(g1, g2, result_graph)
    add_annotations(g1, g1_name, 'g1')
    add_annotations(g2, g2_name, 'g2')
    add_annotations(result_graph, rg_name, 'rg')
    return g1, g1_name, g2, g2_name, result_graph, rg_name

