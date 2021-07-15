from utility_functions import pad_prefix
from plot_graph import plot_graph
from build_graph import build_graph
from compare_graphs import compare_graphs


'''
g_test = build_graph("turtle/test/this_is_a_test_all.ttl")
print("Number of triplets:", len(g_test))
for s, p, o in g_test:
    print(pad_prefix(s, g_test), pad_prefix(p, g_test), pad_prefix(o, g_test))
# plot_graph(g_test)

print("-" * 150)  # #########################################################
'''

g1 = build_graph("turtle/en_it_en_sentence2.ttl")
# g1 = build_graph("turtle/EN_IT_EN.ttl")
print("EN -> IT -> EN")
print("Number of triplets:", len(g1))
for s, p, o in g1:
    print(pad_prefix(s, g1), pad_prefix(p, g1), pad_prefix(o, g1))
# plot_graph(g1)

print("-" * 150)  # #########################################################

g2 = build_graph("turtle/en_sentence2.ttl")
# g2 = build_graph("turtle/EN.ttl")
print("EN")
print("Number of triplets:", len(g2))
for s, p, o in g2:
    print(pad_prefix(s, g2), pad_prefix(p, g2), pad_prefix(o, g2))
# plot_graph(g2)

print("-" * 150)  # #########################################################

# Generate the knowledge graph containing the semantic comparison between g1, g2
rg = compare_graphs(g1, g2)
for s, p, o in rg:
    print(pad_prefix(s, rg), pad_prefix(p, rg), pad_prefix(o, rg))
