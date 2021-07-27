from utilities import constants
from utilities.utility_functions import prefix, check_nodes_synonymy, sub_super_classes, equivalence_classified, hierarchy_classified

def class_subclass_equivalence(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers):
    # Find out two related objects, based on:
    # - relation with same object, but not hierarchically equivalent (e.g. dbpedia individual-class)
    # - same lemma, and of two class types which are one descendant of the other (e.g. nevertheless)
    # - same lemma, and of two class types which have the same ancestor in a single-branch chain (e.g. disaster)

    frontiers_g1, frontiers_g2 = [], []
    list_frontiers = list(map(list, zip(*frontiers)))
    if list_frontiers:
        frontiers_g1, frontiers_g2 = list_frontiers[0], list_frontiers[1]

    print("-------")
    print("dbpedia:")
    # DBPedia
    # Check objects in a "owl:equivalentClass" relation
    for s1,o1 in g1.subject_objects(predicate=constants.EQUIVALENT_CLASS_PREDICATE):
        is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
        node1 = None
        # Check same object in a "owl:sameAs" relation
        for s2,o2 in g2.subject_objects(predicate=constants.SAME_AS_PREDICATE):
            is_g2_frontier = s2 in frontiers_g2 or o2 in frontiers_g2
            node2 = None
            if is_g1_frontier or is_g2_frontier:
                if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)):
                    # To match: o2, instance of o1
                    node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], o2
                elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)):
                    # To match: o2, instance of s1
                    node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], o2
                elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)):
                    # To match: s2, instance of o1
                    node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, o1)][0], s2
                elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)):
                    # To match: s2, instance of s1
                    node1, node2 = [i for i in g1.subjects(constants.TYPE_PREDICATE, s1)][0], s2

                # Add nodes to result graph and to new frontier
                if (node1 and node2) and not equivalence_classified(node1, node2, result_graph):
                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))
                    result_graph.add((node1, constants.EQUIVALENCE_PREDICATE, node2))
                    new_frontiers.add((node1, node2))

    # Check objects in a "owl:sameAs" relation
    for s1,o1 in g1.subject_objects(predicate=constants.SAME_AS_PREDICATE):
        is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
        node1 = None
        # Check same object in a "owl:equivalentClass" relation
        for s2,o2 in g2.subject_objects(predicate=constants.EQUIVALENT_CLASS_PREDICATE):
            is_g2_frontier = s2 in frontiers_g2 or o2 in frontiers_g2
            node2 = None
            if is_g1_frontier or is_g2_frontier:
                if prefix(s2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)):
                    # To match: o1, instance of o2
                    node1, node2 = o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]
                elif prefix(s2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)):
                    # To match: s1, instance of o2
                    node1, node2 = s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, o2)][0]
                elif prefix(o2, g2) == prefix(s1, g1) and ('dbpedia' in prefix(s1, g1)):
                    # To match: o1, instance of s2
                    node1, node2 = o1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]
                elif prefix(o2, g2) == prefix(o1, g1) and ('dbpedia' in prefix(o1, g1)):
                    # To match: s1, instance of s2
                    node1, node2 = s1, [i for i in g2.subjects(constants.TYPE_PREDICATE, s2)][0]

                # Add nodes to result graph and to new frontier
                if (node1 and node2) and not equivalence_classified(node1, node2, result_graph):
                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))
                    result_graph.add((node1, constants.EQUIVALENCE_PREDICATE, node2))
                    new_frontiers.add((node1, node2))

    print("-------")
    print("class_subclass:")
    print(f"frontiers: {[(prefix(i,g1), prefix(j, g2)) for i,j in frontiers]}")
    # class-subclass + single-branch chain
    for node1, node2 in frontiers:
        lemma_1, lemma_2 = lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))]
        classes_1, classes_2 = sub_super_classes(node1, g1), sub_super_classes(node2, g2)

#        # Check if lemma is null
#        if lemma_1 != "":
#            # Check if lemmas are either equal or synonyms
#            if lemma_1==lemma_2 or check_nodes_synonymy(g1, g2, lemmas, node1, None, node2, None):
        # If same hierarchy, relate the classes pairwise and the nodes
        if classes_1==classes_2:
            for cl_1, cl_2 in zip(classes_1, classes_2):
                if not equivalence_classified(cl_1, cl_2, result_graph):
                    # Add each pair of classes to the result graph
                    result_graph.add((cl_1, constants.EQUIVALENCE_PREDICATE, cl_2))
                    # Populate frontier
                    new_frontiers.add((cl_1, cl_2))
                    print("Equivalent:", prefix(cl_1, g1), prefix(cl_2, g2))
            if not equivalence_classified(node1, node2, result_graph):
                # Add the two nodes to the result graph
                result_graph.add((node1, constants.EQUIVALENCE_PREDICATE, node2))
                # Populate frontier
                new_frontiers.add((node1, node2))
                print("Equivalent:", prefix(node1, g1), prefix(node2, g2))
    
        # Otherwise - if the two lists of superclasses share a sublist - create a hierarchy relationship
        else:
            for cl_idx_1, cl_1 in enumerate(classes_1):
                for cl_idx_2, cl_2 in enumerate(classes_2):
                    if (equivalence_classified(cl_1, cl_2, result_graph) or cl_1==cl_2 or check_nodes_synonymy(g1, g2, lemmas, cl_1, None, cl_2, None)) and not (
                        hierarchy_classified(classes_1[cl_idx_1], classes_2[cl_idx_2], n, result_graph)):
    
                        # Create a hierarchy relationship
    
                        # "hierarchy_i" is a reification of a N-ary relationship
                        hierarchy_1 = "hierarchy_" + next(indexes["hierarchies"])
                        hierarchy_2 = "hierarchy_" + next(indexes["hierarchies"])
    
                        # Store class trees for printing
                        h1_classes, h2_classes = [], []
    
                        # Add root class
                        result_graph.add((n[hierarchy_1], n.root, classes_1[cl_idx_1]))
                        result_graph.add((n[hierarchy_2], n.root, classes_2[cl_idx_2]))
                        print("Equivalent:", prefix(classes_1[cl_idx_1], g1), prefix(classes_2[cl_idx_2], g2))
                        result_graph.add((classes_1[cl_idx_1], constants.EQUIVALENCE_PREDICATE, classes_2[cl_idx_2]))
                        h1_classes.append(prefix(classes_1[cl_idx_1], g1))
                        h2_classes.append(prefix(classes_2[cl_idx_2], g2))
    
                        # Add level classes
                        cl_len_1, cl_len_2 = len(classes_1[cl_idx_1:]), len(classes_2[cl_idx_2:])
                        min_len = min(cl_len_1, cl_len_2)
                        max_len = max(cl_len_1, cl_len_2)

                        # Add paired classes
                        for cl_idx in range(min_len-1):
                            class_1, class_2 = classes_1[cl_idx_1+cl_idx+1], classes_2[cl_idx_2+cl_idx+1]
                            if class_1 == class_2 and not equivalence_classified(class_1, class_2, result_graph):
                                print("Equivalent:", prefix(class_1, g1), prefix(class_2, g2))
                                result_graph.add((class_1, constants.EQUIVALENCE_PREDICATE, class_2))
        
                            elif check_nodes_synonymy(g1, g2, lemmas, class_1, None, class_2, None) and not (
                                equivalence_classified(class_1, class_2, result_graph)):
                                print("Synonymy:", prefix(class_1, g1), prefix(class_2, g2))
                                result_graph.add((class_1, n.synonymy, class_2))
                            
                            result_graph.add((n[hierarchy_1], n["level_"+str(cl_idx+1)], class_1))
                            result_graph.add((n[hierarchy_2], n["level_"+str(cl_idx+1)], class_2))
                            h1_classes.append(prefix(class_1, g1))
                            h2_classes.append(prefix(class_2, g2))

                        # Add remaining unpaired classes (from one single graph)
                        if max_len > min_len:
                            if max_len == cl_len_1:
                                for cl_idx in range(max_len-min_len):
                                    result_graph.add((n[hierarchy_1], n["level_"+str(min_len+cl_idx)], classes_1[min_len+cl_idx]))
                                    h1_classes.append(prefix(classes_1[min_len+cl_idx], g1))
                            elif max_len == cl_len_2:
                                for cl_idx in range(max_len-min_len):
                                    result_graph.add((n[hierarchy_2], n["level_"+str(min_len+cl_idx)], classes_2[min_len+cl_idx]))
                                    h2_classes.append(prefix(classes_2[min_len+cl_idx], g2))
    
                        # Add the two hierarchies to the result graph
                        result_graph.add((n[hierarchy_1], n.same_hierarchy, n[hierarchy_2]))
                        if not equivalence_classified(node1, node2, result_graph):
                            # Add the two nodes to the result graph
                            result_graph.add((node1, constants.EQUIVALENCE_PREDICATE, node2))
                            # Populate frontier
                            new_frontiers.add((node1, node2))
                        print("Hierarchy:", prefix(node1, g1), prefix(node2, g2),
                              f"({h1_classes}, {h2_classes})")

                        # Prevent redundant hierarchies:
                        # break inner loop
                        break
                # Continue if loop was not broken
                else:
                    continue
                # Inner loop was broken: broken also outer loop
                break
    
    