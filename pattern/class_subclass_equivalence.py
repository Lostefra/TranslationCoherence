from utilities import constants
from utilities.utility_functions import prefix, is_class, equivalence_classified, check_nodes_equivalence, check_nodes_synonymy, add_equivalence_relation, add_synonymy_relation

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
    while(still_classes):
        before = len(classes)
        to_add = list(g.objects(classes[0], constants.SUBCLASS_PREDICATE))
        classes = to_add + classes
        after = len(classes)
        if(after == before):
            still_classes = False
        #print([prefix(c, g) for c in classes])

    # If node is a class, add also subclasses
    if is_node_class:
        still_classes = True
        while(still_classes):
            before = len(classes)
            to_add = list(g.subjects(constants.SUBCLASS_PREDICATE, classes[-1]))
            classes = classes + to_add
            after = len(classes)
            if(after == before):
                still_classes = False
        
    # If node is an individual, filter out classes with more than one instance
    else:
        classes = filter(lambda x: len(list(g.subjects(constants.TYPE_PREDICATE, x))) < 2, classes)


    return list(filter(lambda x: prefix(x,g) not in unwanted_superclasses, classes))

def equivalent_classes(g1, g2, lemmas, classes):
    equivalences = []
    for class_1, class_2 in classes:
        if check_nodes_equivalence(g1, g2, lemmas, class_1, class_2, None, None):
            equivalences.append(constants.EQUIVALENCE_PREDICATE)
        elif check_nodes_synonymy(g1, g2, lemmas, class_1, class_2, None, None):
            equivalences.append(constants.SYNONYMY_PREDICATE)
        else:
            return False
    return equivalences

def hierarchy_classified(class_1, class_2, n, result_graph):
    h_1 = list(result_graph.subjects(n.root, class_1))
    h_2 = list(result_graph.subjects(n.root, class_2))
    if h_1 and h_2 and any([(h1, n.same_hierarchy, h2) in result_graph for h1 in h_1 for h2 in h_2]):
        return True
    return False

def class_subclass_equivalence(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers):
    # Find out two related objects, based on:
    # - relation with same object, but not hierarchically equivalent (e.g. dbpedia individual-class)
    # - present in frontier, and of two class types which are one descendant of the other (e.g. nevertheless suffer --- suffer)
    # - present in frontier, and of two class types which have the same ancestor in a single-branch chain (e.g. disaster)
    # - present in frontier, and belonging to (or representing) two synonym classes (e.g. nevertheless suffer - still suffer)

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
                if (node1 and node2):
                    add_equivalence_relation(node1, node2, result_graph, new_frontiers)
                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))

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
                if (node1 and node2):
                    add_equivalence_relation(node1, node2, result_graph, new_frontiers)
                    print("Equivalent:", prefix(node1, g1), prefix(node2, g2))


    print("-------")
    print("class_subclass:")
#    print(f"frontiers: {[((prefix(i,g1), is_class(i,g1)), (prefix(j, g2), is_class(j,g2))) for i,j in frontiers]}")
    # class-subclass + single-branch chain
    for node1, node2 in frontiers:
        print("node1, node2", prefix(node1, g1), prefix(node2, g2))

        # Extract superclasses (and subclasses in case of classes)
        classes_1, classes_2 = sub_super_classes(node1, g1), sub_super_classes(node2, g2)
        print(f"classes: {[prefix(i, g1) for i in classes_1]}, {[prefix(i, g2) for i in classes_2]}")
        # If node1 and node2 are classes, replace them with their only (eventual) instances, in order to possibly relate them
        if is_class(node1, g1) and is_class(node2, g2):
            instances_1 = list(g1.subjects(constants.TYPE_PREDICATE, node1))
            instances_2 = list(g2.subjects(constants.TYPE_PREDICATE, node2))
            if len(instances_1) == 1 and len(instances_2) == 1:
                node1, node2 = instances_1[0], instances_2[0]

        # If same hierarchy, relate the classes pairwise and the nodes
        equivalences = None
        if len(classes_1) == len(classes_2):
            classes = zip(classes_1, classes_2)
            equivalences = equivalent_classes(g1, g2, lemmas, classes)
        if equivalences:
#            print("node1, node2", prefix(node1, g1), prefix(node2, g2))
#            print("lemma1, lemma2", lemmas[str(g1.label(node1))], lemmas[str(g2.label(node2))])
#            print(f"classes: {[prefix(i, g1) for i in classes_1]}, {[prefix(i, g2) for i in classes_2]}")
#            print(f"equivalences: {equivalences}")
            for equivalence, (cl_1, cl_2) in zip(equivalences,classes):
                # Add each pair of classes to result graph and to new frontier
                if equivalence==constants.EQUIVALENCE_PREDICATE:
                    add_equivalence_relation(cl_1, cl_2, result_graph, new_frontiers)
                    print("Equivalent:", prefix(cl_1, g1), prefix(cl_2, g2))
                elif equivalence==constants.SYNONYMY_PREDICATE:
                    add_synonymy_relation(cl_1, cl_2, result_graph, new_frontiers)
                    print("Synonymy:", prefix(cl_1, g1), prefix(cl_2, g2))
            
            # Add the nodes to result graph and to new frontier
            if check_nodes_equivalence(g1, g2, lemmas, node1, node2, None, None):
                add_equivalence_relation(node1, node2, result_graph, new_frontiers)
                print("Equivalent:", prefix(node1, g1), prefix(node2, g2))
            elif check_nodes_synonymy(g1, g2, lemmas, node1, node2, None, None):
                add_synonymy_relation(node1, node2, result_graph, new_frontiers)
                print("Synonymy:", prefix(node1, g1), prefix(node2, g2))
    
        # Otherwise - if the two lists of superclasses share a sublist - create a hierarchy relationship
        else:
            for cl_idx_1, cl_1 in enumerate(classes_1):
                for cl_idx_2, cl_2 in enumerate(classes_2):
                    # Check if two classes are either already present in graph or equal or synonym, and not already classified in any hierarchy
                    if (equivalence_classified(cl_1, cl_2, result_graph) or check_nodes_equivalence(g1, g2, lemmas,
                                                                                                    cl_1, cl_2, None,
                                                                                                    None)) and not (
                        hierarchy_classified(cl_1, cl_2, n, result_graph)) and (len(classes_1[cl_idx_1:]) > 1 or len(classes_2[cl_idx_2:]) > 1):
    
                        # Create a hierarchy relationship
    
                        # "hierarchy_i" is a reification of a N-ary relationship
                        hierarchy_1 = "hierarchy_" + next(indexes["hierarchies"])
                        hierarchy_2 = "hierarchy_" + next(indexes["hierarchies"])
    
                        # Store class trees for printing
                        h_classes_1, h_classes_2 = [], []
    
                        # Add root classes to hierarchy, result graph, new frontier and class tree
                        result_graph.add((n[hierarchy_1], n.root, cl_1))
                        result_graph.add((n[hierarchy_2], n.root, cl_2))
                        # Root classes can be either equal or synonyms
                        if (cl_1, constants.SYNONYMY_PREDICATE, cl_2) in result_graph:
                            add_synonymy_relation(cl_1, cl_2, result_graph, new_frontiers)
                            print("Synonymy:", prefix(cl_1, g1), prefix(cl_2, g2))
                        else:
                            add_equivalence_relation(cl_1, cl_2, result_graph, new_frontiers)
                            print("Equivalent:", prefix(cl_1, g1), prefix(cl_2, g2))
                        h_classes_1.append(prefix(cl_1, g1))
                        h_classes_2.append(prefix(cl_2, g2))
    
                        # Add level classes
                        cl_len_1, cl_len_2 = len(classes_1[cl_idx_1:]), len(classes_2[cl_idx_2:])
                        min_len = min(cl_len_1, cl_len_2)
                        max_len = max(cl_len_1, cl_len_2)

                        # Add paired classes
                        for cl_idx in range(min_len-1):
                            class_1, class_2 = classes_1[cl_idx_1+cl_idx+1], classes_2[cl_idx_2+cl_idx+1]
                            # Add equivalence relation across classes
                            if check_nodes_equivalence(g1, g2, lemmas, class_1, class_2, None, None):
                                add_equivalence_relation(class_1, class_2, result_graph, new_frontiers)
                                print("Equivalent:", prefix(class_1, g1), prefix(class_2, g2))
                            # Add synonymy relation across classes
                            elif check_nodes_synonymy(g1, g2, lemmas, class_1, class_2, None, None):
                                add_synonymy_relation(class_1, class_2, result_graph, new_frontiers)
                                print("Synonymy:", prefix(class_1, g1), prefix(class_2, g2))
                            
                            # Add levels to hierarchies
                            result_graph.add((n[hierarchy_1], n["level_"+str(cl_idx+1)], class_1))
                            result_graph.add((n[hierarchy_2], n["level_"+str(cl_idx+1)], class_2))
                            h_classes_1.append(prefix(class_1, g1))
                            h_classes_2.append(prefix(class_2, g2))

                        # Add remaining unpaired classes (from one single graph) to hierarchy
                        if max_len > min_len:
                            # Add levels to h_classes_1
                            if max_len == cl_len_1:
                                for cl_idx in range(max_len-min_len):
                                    result_graph.add((n[hierarchy_1], n["level_"+str(min_len+cl_idx)], classes_1[min_len+cl_idx]))
                                    h_classes_1.append(prefix(classes_1[min_len+cl_idx], g1))
                            # Add levels to h_classes_2
                            else:
                                for cl_idx in range(max_len-min_len):
                                    result_graph.add((n[hierarchy_2], n["level_"+str(min_len+cl_idx)], classes_2[min_len+cl_idx]))
                                    h_classes_2.append(prefix(classes_2[min_len+cl_idx], g2))
    
                        # Add the two hierarchies to the result graph
                        result_graph.add((n[hierarchy_1], n.same_hierarchy, n[hierarchy_2]))
                        # Add the nodes to result graph and to new frontier (nodes can be either equal or synonyms)
                        if (node1, constants.SYNONYMY_PREDICATE, node2) in result_graph:
                            add_synonymy_relation(node1, node2, result_graph, new_frontiers)
                            print("Synonymy:", prefix(node1, g1), prefix(node2, g2))
                        else:
                            add_equivalence_relation(node1, node2, result_graph, new_frontiers)
                            print("Equivalent:", prefix(node1, g1), prefix(node2, g2))

                        print(f"Hierarchy: {h_classes_1} : {prefix(node1, g1)}, {h_classes_2} : {prefix(node2, g2)}")

                        # Prevent redundant hierarchies:
                        # break inner loop
                        break
                # Continue if loop was not broken
                else:
                    continue
                # Inner loop was broken: break also outer loop
                break
    
    