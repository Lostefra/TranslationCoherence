import rdflib

from utilities import constants
from utilities.utility_functions import prefix, is_class, equivalence_classified, synonymy_classified, difference_classified, \
    check_nodes_equivalence, check_nodes_synonymy, add_equivalence_relation, add_synonymy_relation, add_binary_difference_relation


def sub_super_classes(node, g):
    unwanted_superclasses = ['dul:Event', 'owl:Class']

    is_node_class = is_class(node, g)

    # If node is a class, itself is the first class
    if is_node_class:
        classes = [node]
    # If node is an individual, its type is the first class
    else:
        classes = list(g.objects(node, constants.TYPE_PREDICATE))
    
    # Superclasses
    still_classes = classes != []
    while still_classes:
        before = len(classes)
        to_add = list(g.objects(classes[0], constants.SUBCLASS_PREDICATE))
        classes = to_add + classes
        after = len(classes)
        if after == before:
            still_classes = False
#        print([prefix(c, g) for c in classes])

    # If node is a class, add also subclasses
    if is_node_class:
        still_classes = True
        while still_classes:
            before = len(classes)
            to_add = list(g.subjects(constants.SUBCLASS_PREDICATE, classes[-1]))
            classes = classes + to_add
            after = len(classes)
            if after == before:
                still_classes = False
        
    # If node is an individual, filter out classes with more than one instance
    else:
        classes = filter(lambda x: len(list(g.subjects(constants.TYPE_PREDICATE, x))) < 2, classes)

    return list(filter(lambda x: prefix(x, g) not in unwanted_superclasses, classes))


def equivalent_classes(g1, g2, lemmas, node1, node2, classes_1, classes_2, indexes, n, result_graph, new_frontiers):
    # Return true if all classes were pairwise related
    if len(classes_1) == len(classes_2):
        classes = list(zip(classes_1, classes_2))
#        print(f"Hierarchy: {[(prefix(i, g1), prefix(j, g2)) for i,j in classes]}")
        for class_1, class_2 in classes:
            #print(f"{prefix(class_1, g1)}, {prefix(class_2, g2)}")
            if check_nodes_equivalence(g1, g2, lemmas, class_1, class_2):
#                print("Equivalent:", prefix(class_1, g1), prefix(class_2, g2))
                add_equivalence_relation(class_1, class_2, result_graph, new_frontiers)
            elif not equivalence_classified(class_1, class_2, result_graph) and check_nodes_synonymy(g1, g2, lemmas, class_1, class_2):
#                print("Synonym:", prefix(class_1, g1), prefix(class_2, g2))
                add_synonymy_relation(class_1, class_2, result_graph, new_frontiers)
            else:
#                print("Different:", prefix(class_1, g1), prefix(class_2, g2))
                return False
        if len(classes_1) > 1 and not hierarchy_classified(g1, g2, n, result_graph, classes_1, classes_2):
            if any([synonymy_classified(class_1, class_2, result_graph) for class_1, class_2 in classes]):
#                print(f"Similar hierarchy: {[prefix(i, g1) for i in classes_1]}, {[prefix(i, g2) for i in classes_2]}")
                add_hierarchy(classes_1, classes_2, indexes, n, result_graph, False)

        # Add the nodes to result graph and to new frontier
        if check_nodes_equivalence(g1, g2, lemmas, node1, node2):
            add_equivalence_relation(node1, node2, result_graph, new_frontiers)
#            print("Equivalent:", prefix(node1, g1), prefix(node2, g2))
        elif not equivalence_classified(node1, node2, result_graph) and check_nodes_synonymy(g1, g2, lemmas, node1, node2):
            add_synonymy_relation(node1, node2, result_graph, new_frontiers)
#            print("Synonym:", prefix(node1, g1), prefix(node2, g2))
    else:
        return False
    return True


def different_classes(g1, g2, lemmas, node1, node2, classes_1, classes_2, indexes, n, result_graph, new_frontiers):
    # Return true if all classes were pairwise related
    if len(classes_1) == len(classes_2):
        classes = list(zip(classes_1, classes_2))
        for class_1, class_2 in classes:
            add_binary_difference_relation(class_1, class_2, result_graph, new_frontiers)
#            print("Different:", prefix(class_1, g1), prefix(class_2, g2))
        if not hierarchy_classified(g1, g2, n, result_graph, classes_1, classes_2) and (
        len(classes_1)>1 or len(classes_2)>1):
            add_hierarchy(classes_1, classes_2, indexes, n, result_graph, True)
        return True
    return False

def add_hierarchy(classes_1, classes_2, indexes, n, result_graph, are_different):
    # "hierarchy_i" is the reification of a n-ary relation
    hierarchy_1 = "hierarchy_" + next(indexes["hierarchies"])
    hierarchy_2 = "hierarchy_" + next(indexes["hierarchies"])

    result_graph.add((n[hierarchy_1], constants.TYPE_PREDICATE,
                      rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Hierarchy")))
    result_graph.add((n[hierarchy_2], constants.TYPE_PREDICATE,
                      rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Hierarchy")))
    
    # Store class trees for printing
    h_classes_1, h_classes_2 = [], []

    # Add relations between classes and hierarchies
    for class_1 in classes_1:
        # Add levels to hierarchies
        result_graph.add((n[hierarchy_1], n.hasHierarchyMember, class_1))
        result_graph.add((class_1, n.isHierarchyMemberOf, n[hierarchy_1]))
        h_classes_1.append(class_1)
    for class_2 in classes_2:
        # Add levels to hierarchies
        result_graph.add((n[hierarchy_2], n.hasHierarchyMember, class_2))
        result_graph.add((class_2, n.isHierarchyMemberOf, n[hierarchy_2]))
        h_classes_2.append(class_2)
    
    # Add the two hierarchies to the result graph
    if are_different:
        result_graph.add((n[hierarchy_1], n.differentHierarchy, n[hierarchy_2]))
    else:
        result_graph.add((n[hierarchy_1], n.similarHierarchy, n[hierarchy_2]))

def hierarchy_classified(g1, g2, n, result_graph, classes_1, classes_2):
    hierarchies = list(result_graph.subject_objects(predicate=n.similarHierarchy)) + \
                  list(result_graph.subject_objects(predicate=n.differentHierarchy))
    classes = list(zip(classes_1, classes_2))
    for h1, h2 in hierarchies:
        for class_1, class_2 in classes:
            if (class_1, n.isHierarchyMemberOf, h1) in result_graph and \
               (class_2, n.isHierarchyMemberOf, h2) in result_graph:
                return True
    return False


def class_subclass_equivalence(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers):
    # Find out relations, based on:
    # - relation with same object, once as class and the other one as individual (e.g. dbpedia:European_parliament) and one of (s1,s2,o1,o2) in frontier
    
    # Propagate relations of (node1, node2) tuple in frontier:
    # - EQUIVALENCE: of same class types, belonging to same hierarchy (e.g. Period, FestivePeriod, PleasantFestivePeriod)
    #           => equivalence relationship between each pair of classes
    # - HIERARCHY: of two class types which have a common ancestor in a single-branch chain (e.g. Truly(Terrible/Appalling)NaturalDisaster, (Nevertheless)Suffer)
    #           => hierarchy relationship + equivalence between every corresponding class (root+levels)
    # - SYNONYMY: belonging to (or representing) two synonym classes (e.g. NeverthelessSuffer - StillSuffer)
    #           => synonymy relationship + eventual equivalence relationship (in this case, Suffer)
    # - DIFFERENCE: classified as different in result_graph
    #           => propagate difference along entire hierarchy of classes (pairwise)

    frontiers_g1, frontiers_g2 = [], []
    list_frontiers = list(map(list, zip(*frontiers)))
    if list_frontiers:
        frontiers_g1, frontiers_g2 = list_frontiers[0], list_frontiers[1]

#    print("-------")
#    print("dbpedia:")
    # DBPedia
    # Check objects in a "owl:equivalentClass" relation
    for s1, o1 in g1.subject_objects(predicate=constants.EQUIVALENT_CLASS_PREDICATE):
        is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
        node1 = None
        # Check same object in a "owl:sameAs" relation
        for s2, o2 in g2.subject_objects(predicate=constants.SAME_AS_PREDICATE):
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
                if node1 and node2:
                    add_equivalence_relation(node1, node2, result_graph, new_frontiers)
#                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))

    # Check objects in a "owl:sameAs" relation
    for s1, o1 in g1.subject_objects(predicate=constants.SAME_AS_PREDICATE):
        is_g1_frontier = s1 in frontiers_g1 or o1 in frontiers_g1
        node1 = None
        # Check same object in a "owl:equivalentClass" relation
        for s2, o2 in g2.subject_objects(predicate=constants.EQUIVALENT_CLASS_PREDICATE):
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
                if node1 and node2:
                    add_equivalence_relation(node1, node2, result_graph, new_frontiers)
#                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))


#    print("-------")
#    print("class_subclass:")
#    print(f"frontiers: {[((prefix(i,g1), is_class(i,g1)), (prefix(j, g2), is_class(j,g2))) for i,j in frontiers]}")
    # class-subclass + single-branch chain
    for node1, node2 in frontiers:
#        print("node1, node2", prefix(node1, g1), prefix(node2, g2))

        # Keep track of classified difference
        are_different = difference_classified(node1, node2, result_graph)

        # Extract superclasses (and subclasses in case of classes)
        classes_1, classes_2 = sub_super_classes(node1, g1), sub_super_classes(node2, g2)
#        print(f"classes: {[prefix(i, g1) for i in classes_1]}, {[prefix(i, g2) for i in classes_2]}")
        # If node1 and node2 are classes, replace them with their only (eventual) instances, in order to possibly relate them
        if is_class(node1, g1) and is_class(node2, g2):
            instances_1 = list(g1.subjects(constants.TYPE_PREDICATE, node1))
            instances_2 = list(g2.subjects(constants.TYPE_PREDICATE, node2))
            if len(instances_1) == 1 and len(instances_2) == 1:
                node1, node2 = instances_1[0], instances_2[0]

        # If same/synonym hierarchy, relate the classes pairwise and the nodes
        if equivalent_classes(g1, g2, lemmas, node1, node2, classes_1, classes_2, indexes, n, result_graph, new_frontiers):
            pass

        # If different nodes, propagate to (equal-length list of) superclasses
        elif are_different and different_classes(g1, g2, lemmas, node1, node2, classes_1, classes_2, indexes, n, result_graph, new_frontiers):
            pass
    
        # Otherwise - if classes are not already classified in any hierarchy - search for equivalences/differences
        elif not (hierarchy_classified(g1, g2, n, result_graph, classes_1, classes_2)):
            for cl_idx_1, cl_1 in enumerate(classes_1):
                for cl_idx_2, cl_2 in enumerate(classes_2):
                    cl_len_1, cl_len_2 = len(classes_1[cl_idx_1:]), len(classes_2[cl_idx_2:])
                    are_equivalent = equivalence_classified(cl_1, cl_2, result_graph) or check_nodes_equivalence(g1, g2, lemmas, cl_1, cl_2)
                    are_synonymy = synonymy_classified(cl_1, cl_2, result_graph)
                    # Check if two classes are either already present in graph or found equivalent (and there is more than one class on either side)
                    # or the two instance nodes are classified as different
                    if (cl_len_1 > 1 or cl_len_2 > 1) and (are_equivalent or are_synonymy or are_different):
    
                        # Create a hierarchy relationship
#                        print(f"Same hierarchy ({are_different}): {[prefix(i, g1) for i in classes_1]}, {[prefix(i, g2) for i in classes_2]}")
#                        print(f"sub_super_classes: {[prefix(i, g1) for i in sub_super_classes(cl_1, g1)]}, {[prefix(i, g2) for i in sub_super_classes(cl_2, g2)]}")
                        add_hierarchy(classes_1[cl_idx_1:], classes_2[cl_idx_2:], indexes, n, result_graph, are_different)
    
                        # Add root classes to result graph and class tree

                        # Root classes can be either equal or synonyms or different
                        if are_different:
                            add_binary_difference_relation(cl_1, cl_2, result_graph, new_frontiers)
#                            print("Different:", prefix(cl_1, g1), prefix(cl_2, g2))
                        elif are_equivalent:
                            add_equivalence_relation(cl_1, cl_2, result_graph, new_frontiers)
#                            print("Equivalent:", prefix(cl_1, g1), prefix(cl_2, g2))
                        elif not equivalence_classified(cl_1, cl_2, result_graph) and check_nodes_synonymy(g1, g2, lemmas, cl_1, cl_2):
                            add_synonymy_relation(cl_1, cl_2, result_graph, new_frontiers)
#                            print("Synonym:", prefix(cl_1, g1), prefix(cl_2, g2))


                        # Add relations between correspondent classes
                        min_len = min(cl_len_1, cl_len_2)

                        for cl_idx in range(min_len-1):
                            class_1, class_2 = classes_1[cl_idx_1+cl_idx+1], classes_2[cl_idx_2+cl_idx+1]
                            # Add equivalence relation across classes
                            if are_different:
                                add_binary_difference_relation(class_1, class_2, result_graph, new_frontiers)
#                                print("Different:", prefix(class_1, g1), prefix(class_2, g2))
                            elif check_nodes_equivalence(g1, g2, lemmas, class_1, class_2):
                                add_equivalence_relation(class_1, class_2, result_graph, new_frontiers)
#                                print("Equivalent:", prefix(class_1, g1), prefix(class_2, g2))
                            # Add synonymy relation across classes
                            elif not equivalence_classified(class_1, class_2, result_graph) and check_nodes_synonymy(g1, g2, lemmas, class_1, class_2):
                                add_synonymy_relation(class_1, class_2, result_graph, new_frontiers)
#                                print("Synonym:", prefix(class_1, g1), prefix(class_2, g2))

#                        print(f"hierarchy: {[prefix(h,g1) for h in h_classes_1]} : {prefix(node1, g1)},\
#                            {[prefix(h,g2) for h in h_classes_2]} : {prefix(node2, g2)}")

                        # Prevent redundant hierarchies:
                        # break inner loop
                        break
                # Continue if loop was not broken
                else:
                    continue
                # Inner loop was broken: break also outer loop
                break
    
    