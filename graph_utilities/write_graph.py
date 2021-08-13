import rdflib
from rdflib import Namespace, URIRef

from utilities.constants import NAMESPACES
from utilities.utility_functions import pad_prefix, prefix, change_prefix
from utilities import constants


def complete_graph(g1, g2, result_graph):
    ps = [constants.TYPE_PREDICATE, constants.SUBCLASS_PREDICATE]
    # Add type information for graph g1 in result_graph
    for s in result_graph.subjects():
        for p in ps:
            os = list(g1.objects(subject=s, predicate=p))
            for o in os:
                result_graph.add((s, p, o))
                # print(pad_prefix(s, result_graph), pad_prefix(p, result_graph), pad_prefix(o, result_graph))
    # Add type information for graph g2 in result_graph
    for s in result_graph.objects():
        for p in ps:
            os = list(g2.objects(subject=s, predicate=p))
            for o in os:
                result_graph.add((s, p, o))
                # print(pad_prefix(s, result_graph), pad_prefix(p, result_graph), pad_prefix(o, result_graph))

    # Add object property information in result_graph
    for p in result_graph.predicates():
        result_graph.add((p, constants.TYPE_PREDICATE, rdflib.OWL.ObjectProperty))


def replace_s_o(g1, n1, g2, n2, graph, s, p, o):
    graph.remove((s, p, o))
    found = False
    if s in g1.all_nodes() and o in g1.all_nodes():
        graph.add((change_prefix(s, n1), p, change_prefix(o, n1)))
        found = True
    if s in g2.all_nodes() and o in g2.all_nodes():
        graph.add((change_prefix(s, n2), p, change_prefix(o, n2)))
        found = True
    if not found:
        raise ValueError(str(s) + " or " + str(o) + " is not present in the graphs g1 g2.")


def replace_s(g1, n1, g2, n2, graph, s, p, o):
    graph.remove((s, p, o))
    found = False
    if s in g1.all_nodes():
        graph.add((change_prefix(s, n1), p, o))
        found = True
    if s in g2.all_nodes():
        graph.add((change_prefix(s, n2), p, o))
        found = True
    if not found:
        raise ValueError(str(s) + " is not present in the graphs g1 g2.")


def substitute_invalid_IRI(graph, mode, g1_name, g2_name, g1, g2, transl_coher):

    for s, p, o in graph:

        # Handle result_graph #######################################################################################
        if mode == "rg":
            # Handle predicates: subClassOf, type
            if prefix(s, graph).startswith("fred:") and (prefix(p, graph) == "rdfs:subClassOf" or prefix(p, graph) == "rdf:type") and prefix(o, graph).startswith("fred:"):
                replace_s_o(g1, transl_coher[g1_name], g2, transl_coher[g2_name], graph, s, p, o)
            elif prefix(s, graph).startswith("fred:") and (prefix(p, graph) == "rdfs:subClassOf" or prefix(p, graph) == "rdf:type"):
                replace_s(g1, transl_coher[g1_name], g2, transl_coher[g2_name], graph, s, p, o)
            elif prefix(s, graph).startswith("transl_coher:") and prefix(p, graph) == "rdf:type" and prefix(o, graph) == "owl:ObjectProperty":
                graph.remove((s, p, o))
                graph.add((change_prefix(s, constants.NAMESPACES["translation_coherence_vocabulary"]), p, o))
            # Handle different_expression pattern
            elif prefix(s, graph).startswith("transl_coher:expression_") and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("transl_coher:expression_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_") and int(prefix(s, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_") and int(prefix(s, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, constants.NAMESPACES["translation_coherence_vocabulary"]), p, o))
            # Handle similar_hierarchy pattern (isHierarchyMemberOf, hasHierarchyMember)
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("transl_coher:hierarchy_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(o, graph).startswith("transl_coher:hierarchy_") and int(prefix(o, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:isHierarchyMemberOf") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(o, graph).startswith("transl_coher:hierarchy_") and int(prefix(o, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:isHierarchyMemberOf") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and int(prefix(s, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:hasHierarchyMember") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and int(prefix(s, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:hasHierarchyMember") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            # Handle only_in pattern
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph) == "transl_coher:onlyIn" and prefix(o, graph) == "transl_coher:g1":
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           transl_coher[g1_name]))
            elif prefix(p, graph) == "transl_coher:onlyIn" and prefix(o, graph) == "transl_coher:g1":
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]), transl_coher[g1_name]))
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph) == "transl_coher:onlyIn" and prefix(o, graph) == "transl_coher:g2":
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           transl_coher[g2_name]))
            elif prefix(p, graph) == "transl_coher:onlyIn" and prefix(o, graph) == "transl_coher:g2":
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]), transl_coher[g2_name]))
            # Handle predicates: equivalent, starting_point, synonymy, different_context
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("transl_coher:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]), o))
            elif prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]), change_prefix(o, transl_coher[g2_name])))
            elif p == constants.STARTING_POINT_PREDICATE or p == constants.EQUIVALENCE_PREDICATE or p == constants.DIFFERENT_CONTEXT_PREDICATE or p == constants.SYNONYMY_PREDICATE:
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]), o))
        # #######################################################################################

        # Handle g1 #######################################################################################
        elif mode == "g1":
            if prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("fred:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, transl_coher[g1_name]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, transl_coher[g1_name]), o))
            elif prefix(p, graph).startswith("fred:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, transl_coher[g1_name]), change_prefix(o, transl_coher[g1_name])))
            elif prefix(o, graph).startswith("fred:") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), p, change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), p, o))
            elif prefix(p, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, transl_coher[g1_name]), o))
            elif prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, p, change_prefix(o, transl_coher[g1_name])))
        # #######################################################################################

        # Handle g2 #######################################################################################
        elif mode == "g2":
            if prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("fred:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, transl_coher[g2_name]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("fred:") and prefix(p, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, transl_coher[g2_name]), o))
            elif prefix(p, graph).startswith("fred:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, transl_coher[g2_name]), change_prefix(o, transl_coher[g2_name])))
            elif prefix(o, graph).startswith("fred:") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), p, change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), p, o))
            elif prefix(p, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, change_prefix(p, transl_coher[g2_name]), o))
            elif prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((s, p, change_prefix(o, transl_coher[g2_name])))
        # #######################################################################################

        else:
            raise ValueError("Mode must be in: rg, g1, g2.")

    return graph


def write_graph(g1, g2, result_graph, lang_1, lang_2, sentence, format='xml'):
    # Write graph to file
    # complete_graph(g1, g2, result_graph)

    lang_1 = lang_1.split("/")[1]
    lang_2 = lang_2.split("/")[1]
    rg_name = lang_1 + '_VS_' + lang_2 + '__' + sentence + ".owl"
    g1_name = lang_1 + '__' + sentence + ".owl"
    g2_name = lang_2 + '__' + sentence + ".owl"
    destination_result_graph = 'ontology/' + rg_name
    destination_g1 = 'ontology/' + g1_name
    destination_g2 = 'ontology/' + g2_name

    transl_coher = Namespace(NAMESPACES["translation_coherence"])
    result_graph_clean = substitute_invalid_IRI(result_graph, "rg", g1_name, g2_name, g1, g2, transl_coher)
    g1_clean = substitute_invalid_IRI(g1, "g1", g1_name, g2_name, g1, g2, transl_coher)
    g2_clean = substitute_invalid_IRI(g2, "g2", g1_name, g2_name, g1, g2, transl_coher)

    result_graph_clean.add((transl_coher[rg_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareOntology"), transl_coher[g1_name]))
    result_graph_clean.add((transl_coher[rg_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareOntology"), transl_coher[g2_name]))
    result_graph_clean.add((transl_coher[g1_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareWith"), transl_coher[g2_name]))

    print("-" * 150)  # #########################################################
    print("Graph with valid IRIs:")
    # Ordered printing:
    graph = result_graph_clean
    for p in sorted(set(graph.predicates())):
        for s, o in graph.subject_objects(predicate=p):
            print(pad_prefix(s, graph), pad_prefix(p, graph), pad_prefix(o, graph))

    print("-" * 150)  # #########################################################
    print("Serializing graphs...")
    result_graph_clean.serialize(destination=destination_result_graph, format=format)
    g1_clean.serialize(destination=destination_g1, format=format)
    g2_clean.serialize(destination=destination_g2, format=format)
