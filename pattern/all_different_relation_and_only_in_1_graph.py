from rdflib.term import Literal

from utilities import constants
from utilities.utility_functions import get_node_triples


def all_different_relations_and_only_in_1_graph(g1, g2, n, rg, lemmas):
    rg1 = set()
    rg2 = set()
    for p in [n.starting_point, n.equivalent, n.synonymy, n.different]:
        for s, o in rg.subject_objects(predicate=p):
            rg1.add(s)
            rg2.add(o)
    left_out_g1 = set()
    left_out_g2 = set()
    for node in g1.all_nodes() - rg1:
        if type(node) is not Literal and not str(node).startswith(constants.DBPEDIA_PREFIX):
            left_out_g1.add(node)
    for node in g2.all_nodes() - rg2:
        if type(node) is not Literal and not str(node).startswith(constants.DBPEDIA_PREFIX):
            left_out_g2.add(node)

    for node_1 in left_out_g1:
        label = lemmas[str(g1.label(node_1))]
        # only_in_1_graph
        if (label != "" and label not in [lemmas[str(g2.label(node_2))] for node_2 in g2.all_nodes()]) or \
                (label == "" and node_1 not in g2.all_nodes()):
            rg.add((node_1, n.onlyIn, n.g1))
        # all_different_relations
        else:
            node_triples_1 = get_node_triples(node_1, g1)
            node_triples_2 = get_node_triples(node_1, g2)
            if node_triples_1 and node_triples_2:
                found_equal_relation = False
                for triple_1 in node_triples_1:
                    if triple_1 in node_triples_2:
                        found_equal_relation = True
                        break
                if not found_equal_relation:
                    rg.add((node_1, n.differentContext, node_1))

    for node_2 in left_out_g2:
        label = lemmas[str(g2.label(node_2))]
        # only_in_1_graph
        if (label != "" and label not in [lemmas[str(g1.label(node_1))] for node_1 in g1.all_nodes()]) or \
                (label == "" and node_2 not in g1.all_nodes()):
            rg.add((node_2, n.onlyIn, n.g2))
        # all_different_relations
        else:
            node_triples_1 = get_node_triples(node_2, g1)
            node_triples_2 = get_node_triples(node_2, g2)
            if node_triples_1 and node_triples_2:
                found_equal_relation = False
                for triple_2 in node_triples_2:
                    if triple_2 in node_triples_1:
                        found_equal_relation = True
                        break
                if not found_equal_relation:
                    rg.add((node_2, n.differentContext, node_2))

