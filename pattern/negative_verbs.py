import rdflib

from utilities.utility_functions import prefix, add_equivalence_relation, check_nodes_synonymy, check_nodes_equivalence, \
    add_synonymy_relation
from utilities.wordnet_utility_functions import check_synonymy
import utilities.constants as constants


def negative_verbs(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers, mode):
    # Identify verbs which give a negative meaning to the expressions
    frontiers_g1, frontiers_g2 = [], []
    list_frontiers = list(map(list, zip(*frontiers)))
    if list_frontiers and mode == 1:
        frontiers_g1, frontiers_g2 = list_frontiers[0], list_frontiers[1]
    elif list_frontiers and mode == 2:
        frontiers_g1, frontiers_g2 = list_frontiers[1], list_frontiers[0]
    for s1, p1, o1 in g1:
        if "fred:fail" in prefix(s1, g1) and prefix(p1, g1) == "vn.role:Theme":
            is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
            for s2, p2, o2 in g2:
                is_g2_frontier = s2 in frontiers_g2 or o2 in frontiers_g2
                are_equivalent = check_nodes_equivalence(g1, g2, lemmas, o1, s2)
                are_synonyms = check_nodes_synonymy(g1, g2, lemmas, o1, s2)
                if (is_g1_frontier or is_g2_frontier) and \
                        (are_equivalent or are_synonyms) and \
                        prefix(p2, g2) == "boxing:hasTruthValue" and prefix(o2, g2) == "boxing:False":
                    # "Expression_i" is a reification of a N-ary relationship
                    expr1 = "expression_" + next(indexes["expressions"])
                    expr2 = "expression_" + next(indexes["expressions"])

                    result_graph.add((n[expr1], n.involvesAuxiliaryVerb, s1))
                    result_graph.add((n[expr1], n.involvesVerb, o1))

                    result_graph.add((n[expr2], p2, o2))
                    result_graph.add((n[expr2], n.involvesVerb, s2))

                    result_graph.add((n[expr1], n.differentExpression, n[expr2]))
                    result_graph.add((n[expr1], constants.TYPE_PREDICATE,
                                      rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))
                    result_graph.add((n[expr2], constants.TYPE_PREDICATE,
                                      rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))

                    if are_equivalent:
                        add_equivalence_relation(o1, s2, result_graph, new_frontiers)
                    else:
                        add_synonymy_relation(o1, s2, result_graph, new_frontiers)
