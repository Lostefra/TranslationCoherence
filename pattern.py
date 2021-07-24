import constants
from utility_functions import prefix, superclasses, check_nodes_synonymy


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
                if (is_g1_frontier or is_g2_frontier) and lemmas[str(g1.label(o1))] == lemmas[str(g2.label(s2))] and \
                        prefix(p2, g2) == "boxing:hasTruthValue" and prefix(o2, g2) == "boxing:False":
                    # "Expression_i" is a reification of a N-ary relationship
                    expr1 = "expression_" + next(indexes["expressions"])
                    expr2 = "expression_" + next(indexes["expressions"])

                    result_graph.add((n[expr1], n.involves_aux, s1))
                    result_graph.add((n[expr1], n.involves_verb, o1))

                    result_graph.add((n[expr2], p2, o2))
                    result_graph.add((n[expr2], n.involves_verb, s2))

                    result_graph.add((n[expr1], n.same_expression, n[expr2]))

                    if (o1, n.equivalent, s2) not in result_graph:
                        result_graph.add((o1, n.equivalent, s2))
                        print("RG aggiunto materialise_1")
                    new_frontiers.add((o1, s2))


def class_subclass_equivalence(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers):
    # Find out two related objects, based on:
    # - relation with same object, but not hierarchically equivalent (e.g. dbpedia individual-class)
    # - same label, and of two class types which are one descendant of the other (e.g. nevertheless)
    # - same label, and of two class types which have the same ancestor in a single-branch chain (e.g. disaster)

    frontiers_g1, frontiers_g2 = [], []
    list_frontiers = list(map(list, zip(*frontiers)))
    if list_frontiers:
        frontiers_g1, frontiers_g2 = list_frontiers[0], list_frontiers[1]

    print("-------")
    print("dbpedia:")
    #DBPedia
    for s1, p1, o1 in g1:
        is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
        node1, node2 = None, None
        if prefix(p1, g1) == "owl:equivalentClass":
            # Check same object in a "owl:sameAs" relation
            for s2, p2, o2 in g2:
                is_g2_frontier = s2 in frontiers_g2 or o2 in frontiers_g2
                if is_g1_frontier or is_g2_frontier:
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: o2, instance of o1
                        node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], o2
                        #to_match.append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], o2))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: o2, instance of s1
                        node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], o2
                        #to_match.append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], o2))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: s2, instance of o1
                        node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], s2
                        #to_match.append(([i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], s2))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:sameAs"):
                        # To match: s2, instance of s1
                        node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], s2
                        #to_match.append(([i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], s2))


        elif prefix(p1, g1) == "owl:sameAs":
            # Check same object in a "owl:equivalentClass" relation
            for s2, p2, o2 in g2:
                is_g2_frontier = s2 in frontiers_g2 or o2 in frontiers_g2
                if is_g1_frontier or is_g2_frontier:
                    if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: o1, instance of o2
                        node1, node2 = o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]
                        #to_match.append((o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]))
                    elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: s1, instance of o2
                        node1, node2 = s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]
                        #to_match.append((s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]))
                    elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: o1, instance of s2
                        node1, node2 = o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]
                        #to_match.append((o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]))
                    elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)) and (
                            prefix(p2, g2) == "owl:equivalentClass"):
                        # To match: s1, instance of s2
                        node1, node2 = s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]
                        #to_match.append((s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]))
        
        # Add nodes to result graph and to new frontier
        if node1 and node2:
            print(prefix(node1, g1), prefix(node2, g2))
            result_graph.add((node1, n.equivalent, node2))
            new_frontiers.add((node1, node2))

    print("-------")
    print("class_subclass:")
    #class-subclass + single-branch chain
    for node1 in g1.all_nodes():
        is_g1_frontier = s1 in frontiers_g1
        lemma_1 = lemmas[str(g1.label(node1))]
        classes_1 = superclasses(node1, g1)
        for node2 in g2.all_nodes():
            is_g2_frontier = s2 in frontiers_g2
            lemma_2 = lemmas[str(g2.label(node2))]          
            classes_2 = superclasses(node2, g2)
            # Check if nodes are in frontier
            if (is_g1_frontier or is_g2_frontier) and lemma_1 is not "":
                # Check if lemmas are either equal or synonyms
                if lemma_1==lemma_2 or check_nodes_synonymy(g1, g2, lemmas, node1, None, node2, None):
                    # If same hierarchy, relate the classes pairwise and the nodes
                    if classes_1==classes_2:
                        for cl_1, cl_2 in zip(classes_1, classes_2):
                            if (cl_1, constants.EQUIVALENT_CLASS_PREDICATE, cl_2) not in result_graph:
                                # Add the two classes to the result graph
                                result_graph.add((cl_1, constants.EQUIVALENT_CLASS_PREDICATE, cl_2))
                        if (node1, constants.SAME_AS_PREDICATE, node2) not in result_graph:
                            # Add the two nodes to the result graph
                            result_graph.add((node1, constants.SAME_AS_PREDICATE, node2))
                            # Populate frontier
                            new_frontiers.add((node1, node2))
                            print("Equal:", prefix(node1, g1), prefix(node2, g2))
    
                    # Otherwise - if the two lists of superclasses share a sublist - create a hierarchy relationship
                    else:
                        for cl_idx_1, cl_1 in enumerate(classes_1):
                            for cl_idx_2, cl_2 in enumerate(classes_2):
                                if cl_1==cl_2 and (node1, constants.SAME_AS_PREDICATE, node2) not in result_graph and (node1, n.hierarchy_equivalent, node2) not in result_graph:
        
                                    # Create a hierarchy relationship
    
                                    # "hierarchy_i" is a reification of a N-ary relationship
                                    hierarchy_1 = "hierarchy_" + next(indexes["hierarchies"])
                                    hierarchy_2 = "hierarchy_" + next(indexes["hierarchies"])
    
                                    # Store class trees for printing
                                    h1_classes, h2_classes = [], []
    
                                    # Add root class
                                    result_graph.add((n[hierarchy_1], n.root, classes_1[cl_idx_1]))
                                    result_graph.add((n[hierarchy_2], n.root, classes_2[cl_idx_2]))
                                    h1_classes.append(prefix(classes_1[cl_idx_1], g1))
                                    h2_classes.append(prefix(classes_2[cl_idx_2], g2))
    
                                    # Add leaf classes
                                    if len(classes_1)>1:
                                        for i,c in enumerate(classes_1[cl_idx_1-1::-1]):
                                            result_graph.add((n[hierarchy_1], n["leaf_"+str(i+1)], c))
                                            h1_classes.append(prefix(c, g1))
                                    if len(classes_2)>2:
                                        for i,c in enumerate(classes_2[cl_idx_2-1::-1]):
                                            result_graph.add((n[hierarchy_2], n["leaf_"+str(i+1)], c))
                                            h2_classes.append(prefix(c, g2))
                                    # Add the two hierarchies to the result graph
                                    result_graph.add((n[hierarchy_1], n.same_hierarchy, n[hierarchy_2]))
                                    # Add the two nodes to the result graph
                                    result_graph.add((node1, n.hierarchy_equivalent, node2))
                                    # Populate frontier
                                    new_frontiers.add((node1, node2))
                                    print("Hierarchy:", prefix(node1, g1), prefix(node2, g2), f"({h1_classes}, {h2_classes})")

