from utilities.utility_functions import pad_prefix
from graph_utilities.build_graph import build_graph
from graph_utilities.compare_graphs import compare_graphs
from graph_utilities.write_graph import write_graph

lang_1 = "en/en"
lang_2 = "it/en_it_en"
sentence = "sentence2"

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
for p in sorted(set(rg.predicates())):
    for s, o in rg.subject_objects(predicate=p):
        print(pad_prefix(s, rg), pad_prefix(p, rg), pad_prefix(o, rg))

print("-" * 150)  # #########################################################

write_graph(g1, g2, rg, lang_1, lang_2, sentence)
