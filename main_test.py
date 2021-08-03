from rdflib import Namespace
from rdflib.term import Literal

from utilities.utility_functions import pad_prefix, lemma
from graph_utilities.build_graph import build_graph
from graph_utilities.compare_graphs import compare_graphs
from graph_utilities.write_graph import write_graph


'''
g_test = build_graph("turtle/test/this_is_a_test_all.ttl")
print("Number of triplets:", len(g_test))
for s, p, o in g_test:
    print(pad_prefix(s, g_test), pad_prefix(p, g_test), pad_prefix(o, g_test))
# plot_graph(g_test)

print("-" * 150)  # #########################################################
'''

g1 = build_graph("EuroParl/Paragraph1/turtle/en/en_sentence2.ttl")
# g1 = build_graph("turtle/EN_IT_EN.ttl")
print("EN -> IT -> EN")
print("Number of triplets:", len(g1))
for s, p, o in g1:
    print(pad_prefix(s, g1), pad_prefix(p, g1), pad_prefix(o, g1))
# plot_graph(g1)

print("-" * 150)  # #########################################################

g2 = build_graph("EuroParl/Paragraph1/turtle/de/en_de_en_sentence2.ttl")
# g2 = build_graph("turtle/EN.ttl")
print("EN")
print("Number of triplets:", len(g2))
for s, p, o in g2:
    print(pad_prefix(s, g2), pad_prefix(p, g2), pad_prefix(o, g2))
# plot_graph(g2)

print("-" * 150)  # #########################################################

# Generate the knowledge graph containing the semantic comparison between g1, g2
rg = compare_graphs(g1, g2)
#for s, p, o in rg:
#    print(pad_prefix(s, rg), pad_prefix(p, rg), pad_prefix(o, rg))

# Ordered printing:
for p in sorted(set(rg.predicates())):
    for s, o in rg.subject_objects(predicate=p):
        print(pad_prefix(s, rg), pad_prefix(p, rg), pad_prefix(o, rg))

write_graph(g1, g2, rg)

# Analyse which are the nodes left out
n = Namespace("http://example.org/translation_coherence/")
rg1 = set()
rg2 = set()
for p in [n.starting_point, n.equivalent]:
    for s, o in rg.subject_objects(predicate=p):
        rg1.add(s)
        rg2.add(o)
left_out_g1 = set()
left_out_g2 = set()
for node in g1.all_nodes() - rg1:
    if type(node) is not Literal:
        left_out_g1.add(node)
for node in g2.all_nodes() - rg2:
    if type(node) is not Literal:
        left_out_g2.add(node)

print("\nG1 not taken nodes: ")
for node in left_out_g1:
    print(node, " : ", g1.label(node), lemma(g1.label(node)))
print("\nG2 not taken nodes: ")
for node in left_out_g2:
    print(node, " : ", g1.label(node), lemma(g1.label(node)))
