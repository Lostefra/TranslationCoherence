from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph


def insert_prefix(node):
    if "#" not in str(node):
        return str(node)
    IRI = str(node).split('#')[0]
    ID = str(node).split('#')[1]
    if IRI == "http://www.ontologydesignpatterns.org/ont/fred/domain.owl":
        return "fred:" + ID
    if IRI == "http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl":
        return "quant:" + ID
    if IRI == "http://www.w3.org/2002/07/owl":
        return "owl:" + ID
    if IRI == "http://www.w3.org/1999/02/22-rdf-syntax-ns":
        return "rdf:" + ID
    else:
        return ":" + ID


def plot_graph(graph):
    G = rdflib_to_networkx_multidigraph(graph)

    # Change labels (use prefix)
    mapping = {}
    for node in G.nodes:
        mapping[node] = insert_prefix(node)
    G = nx.relabel_nodes(G, mapping)

    # Plot Networkx instance of RDF Graph
    pos = nx.spring_layout(G)
    edge_labels = {(edge[0], edge[1]): insert_prefix(edge[2]) for edge in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw(G, pos, with_labels=True)
    plt.show()


if __name__ == "__main__":
    g1 = Graph()
    g1.parse("this_is_a_test_clean.turtle", format="turtle")
    plot_graph(g1)
