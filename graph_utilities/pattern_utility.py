import utilities.constants as constants
from rdflib import term
from utilities.utility_functions import is_class


def add_intensional_reification(class_node, result_graph):
    # create individual of class concept
    transl_coher_prefix = constants.NAMESPACES["translation_coherence"]
    intensional_reification_class_name = class_node.split("/")[-1] + "Concept"
    intensional_reification_graph_name = class_node.split("/")[-2] + "/"
    intensional_reification_class_node = term.URIRef(transl_coher_prefix + intensional_reification_graph_name +
                                                     intensional_reification_class_name)
    result_graph.add((intensional_reification_class_node, constants.TYPE_PREDICATE, constants.CLASS_CONCEPT_CLASS))
    # add translation coherence predicate between the intensional reifications of the classes
    # and remove those between classes
    for p, o in result_graph.predicate_objects(class_node):
        result_graph.add((intensional_reification_class_node, p, o))
        result_graph.remove((class_node, p, o))
    for s, p in result_graph.subject_predicates(class_node):
        result_graph.add((s, p, intensional_reification_class_node))
        result_graph.remove((s, p, class_node))
    # see also
    result_graph.add((intensional_reification_class_node, constants.SEE_ALSO_PREDICATE, class_node))
    # disjointness
    result_graph.add((class_node, constants.DISJOINT_WITH_PREDICATE, constants.CLASS_CONCEPT_CLASS))


def get_intensional_reification(class_node, graph):
    return graph.value(predicate=constants.SEE_ALSO_PREDICATE, object=class_node)


def add_intensional_reifications_parents(graphs, result_graph):
    for graph in graphs:
        for s, o in graph.subject_objects(constants.SUBCLASS_PREDICATE):
            s_individual = get_intensional_reification(s, result_graph)
            o_individual = get_intensional_reification(o, result_graph)
            if s_individual is not None and o_individual is not None:
                result_graph.add((s_individual, constants.PARENT_CLASS_CONCEPT_PREDICATE, o_individual))


def apply_intensional_reification(g1, g2, result_graph):
    for node in result_graph.all_nodes():
        if is_class(node, g1) or is_class(node, g2):
            add_intensional_reification(node, result_graph)
    add_intensional_reifications_parents([g1, g2], result_graph)
