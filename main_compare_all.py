from graph_utilities.pattern_utility import apply_intensional_reification
from utilities.utility_functions import pad_prefix
from graph_utilities.build_graph import build_graph
from graph_utilities.compare_graphs import compare_graphs
from graph_utilities.deploy_graph import serialize_graph, update_graph_iri, add_annotations

lang_1 = "en/en"
lang_2 = "it/en_it_en"
sentence = "sentence4"

g1 = build_graph("EuroParl/Paragraph1/turtle/" + lang_1 + "_" + sentence + ".ttl")
print(lang_1)
print("Number of triplets:", len(g1))
for s, p, o in g1:
    print(pad_prefix(s, g1), pad_prefix(p, g1), pad_prefix(o, g1))

print("-" * 150)  # #########################################################

g2 = build_graph("EuroParl/Paragraph1/turtle/" + lang_2 + "_" + sentence + ".ttl")
print(lang_2)
print("Number of triplets:", len(g2))
for s, p, o in g2:
    print(pad_prefix(s, g2), pad_prefix(p, g2), pad_prefix(o, g2))

print("-" * 150)  # #########################################################

# Generate the knowledge graph containing the semantic comparison between g1, g2
rg = compare_graphs(g1, g2)

# Ordered printing:
graph = rg
for p in sorted(set(graph.predicates())):
    for s, o in graph.subject_objects(predicate=p):
        print(pad_prefix(s, graph), pad_prefix(p, graph), pad_prefix(o, graph))

print("-" * 150)  # #########################################################

g1, g1_name, g2, g2_name, result_graph, rg_name = update_graph_iri(g1, g2, rg, lang_1, lang_2, sentence)
apply_intensional_reification(g1, g2, result_graph)
add_annotations(g1, g1_name, 'g1')
add_annotations(g2, g2_name, 'g2')
add_annotations(result_graph, rg_name, 'rg')
serialize_graph(g1, g1_name, g2, g2_name, result_graph, rg_name, format='pretty-xml')
