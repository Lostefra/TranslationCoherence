from utilities.utility_functions import prefix
from utilities.wordnet_utility_functions import check_synonymy


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
                if (is_g1_frontier or is_g2_frontier) and \
                        check_synonymy(lemmas[str(g1.label(o1))], lemmas[str(g2.label(s2))]) and \
                        prefix(p2, g2) == "boxing:hasTruthValue" and prefix(o2, g2) == "boxing:False":
                    # "Expression_i" is a reification of a N-ary relationship
                    expr1 = "expression_" + next(indexes["expressions"])
                    expr2 = "expression_" + next(indexes["expressions"])

                    result_graph.add((n[expr1], n.involves_aux, s1))
                    result_graph.add((n[expr1], n.involves_verb, o1))

                    result_graph.add((n[expr2], p2, o2))
                    result_graph.add((n[expr2], n.involves_verb, s2))

                    result_graph.add((n[expr1], n.different_expression, n[expr2]))

                    if (o1, n.equivalent, s2) not in result_graph:
                        result_graph.add((o1, n.equivalent, s2))
                    new_frontiers.add((o1, s2))

