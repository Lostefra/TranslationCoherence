import rdflib
from rdflib import Namespace, URIRef
import datetime

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


def substitute_invalid_IRI(graph, rg_name, mode, g1_name, g2_name, g1, g2, transl_coher):

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
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[rg_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_") and int(prefix(s, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_") and int(prefix(s, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("transl_coher:expression_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), p, o))
            # Handle similar_hierarchy pattern (isHierarchyMemberOf, hasHierarchyMember)
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and prefix(p, graph).startswith("transl_coher:") and prefix(o, graph).startswith("transl_coher:hierarchy_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[rg_name])))
            elif prefix(o, graph).startswith("transl_coher:hierarchy_") and int(prefix(o, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:isHierarchyMemberOf") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g1_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[rg_name])))
            elif prefix(o, graph).startswith("transl_coher:hierarchy_") and int(prefix(o, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:isHierarchyMemberOf") and prefix(s, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[g2_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[rg_name])))
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and int(prefix(s, graph)[-1]) % 2 == 1 and prefix(p, graph).startswith("transl_coher:hasHierarchyMember") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g1_name])))
            elif prefix(s, graph).startswith("transl_coher:hierarchy_") and int(prefix(s, graph)[-1]) % 2 == 0 and prefix(p, graph).startswith("transl_coher:hasHierarchyMember") and prefix(o, graph).startswith("fred:"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), change_prefix(p, constants.NAMESPACES["translation_coherence_vocabulary"]),
                           change_prefix(o, transl_coher[g2_name])))
            elif prefix(s, graph).startswith("transl_coher:hierarchy_"):
                graph.remove((s, p, o))
                graph.add((change_prefix(s, transl_coher[rg_name]), p, o))
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


def remove_undesired_triples(graph):
    for s, p, o in graph:
        # if str(s).startswith(constants.OWL_PREFIX) or str(s).startswith(constants.DUL_PREFIX) or \
        #        str(o).startswith(constants.OWL_PREFIX) or str(o).startswith(constants.DUL_PREFIX) or \
        if (str(s).startswith(NAMESPACES["translation_coherence"]) and "docuverse" in str(s)) or \
                (str(o).startswith(NAMESPACES["translation_coherence"]) and "docuverse" in str(o)):
            graph.remove((s, p, o))


def update_graph_iri(g1, g2, result_graph, lang_1, lang_2, sentence):
    # Write graph to file
    # complete_graph(g1, g2, result_graph)

    lang_1 = lang_1.split("/")[1]
    lang_2 = lang_2.split("/")[1]
    rg_name = lang_1 + '_VS_' + lang_2 + '_' + sentence + ".ttl"
    g1_name = lang_1 + '_' + sentence + ".ttl"
    g2_name = lang_2 + '_' + sentence + ".ttl"

    transl_coher = Namespace(NAMESPACES["translation_coherence"])
    result_graph_clean = substitute_invalid_IRI(result_graph, rg_name, "rg", g1_name, g2_name, g1, g2, transl_coher)
    g1_clean = substitute_invalid_IRI(g1, rg_name, "g1", g1_name, g2_name, g1, g2, transl_coher)
    g2_clean = substitute_invalid_IRI(g2, rg_name, "g2", g1_name, g2_name, g1, g2, transl_coher)

    remove_undesired_triples(result_graph_clean)

    result_graph_clean.add((transl_coher[rg_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareOntology"), transl_coher[g1_name]))
    result_graph_clean.add((transl_coher[rg_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareOntology"), transl_coher[g2_name]))
    result_graph_clean.add((transl_coher[g1_name], URIRef(str(constants.NAMESPACES["translation_coherence_vocabulary"]) + "compareWith"), transl_coher[g2_name]))

    # print("-" * 150)  # #########################################################
    # print("Graph with valid IRIs:")
    # # Ordered printing:
    # graph = result_graph_clean
    # for p in sorted(set(graph.predicates())):
    #     for s, o in graph.subject_objects(predicate=p):
    #         print(pad_prefix(s, graph), pad_prefix(p, graph), pad_prefix(o, graph))

    return g1_clean, g1_name, g2_clean, g2_name, result_graph_clean, rg_name


def add_annotations(graph, graph_name, mode):

    graph_ontology = rdflib.term.URIRef(NAMESPACES['translation_coherence'] + graph_name)
    # Ontology
    graph.add((graph_ontology, constants.TYPE_PREDICATE, rdflib.term.URIRef(NAMESPACES['owl']+'Ontology')))
    # Label
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['rdfs']+'label'),
        rdflib.term.Literal(graph_name.split(".")[0])))
    # Title
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['dc']+'title'),
        rdflib.term.Literal(graph_name.split(".")[0])))
    # Imports
    for imported_ontology in constants.IMPORTED_ONTOLOGIES:
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['owl']+'imports'),
            rdflib.term.URIRef(NAMESPACES[imported_ontology])))
    # Language
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['dc']+'language'),
        rdflib.term.URIRef('http://publications.europa.eu/resource/authority/language/ENG')))
    # License
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['dct']+'license'),
        rdflib.term.URIRef('https://creativecommons.org/licenses/by-sa/4.0/')))
    # Creators
    creators = ['Andrea Lavista', 'Lorenzo Mario Amorosa', 'Michele Iannello']
    for creator in creators:
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['dc']+'creator'),
            rdflib.term.Literal(creator)))
    # Date
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['dct']+'issued'),
        rdflib.term.Literal('2021-08-13')))
    graph.add((graph_ontology,
        rdflib.term.URIRef(NAMESPACES['dct']+'modified'),
        rdflib.term.Literal(datetime.date.today().strftime('%Y-%m-%d'))))
    # Textual reference
    if mode != 'rg':
        sentence = graph.value(subject=rdflib.term.URIRef(NAMESPACES['fred'] + 'docuverse'),
                                predicate = rdflib.term.URIRef(NAMESPACES['earmark'] + 'hasContent'))
        # Comment
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['rdfs']+'comment'),
            rdflib.term.Literal(sentence)))
        # Description
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['dc']+'description'),
            rdflib.term.Literal(sentence)))
    else:
        pass
        ont1, ont2 = list(graph.objects(subject=graph_ontology,
            predicate=rdflib.term.URIRef(NAMESPACES['translation_coherence_vocabulary']+'compareOntology')))
        ont1, ont2 = str(ont1), str(ont2)
        # Comment
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['rdfs']+'comment'),
            rdflib.term.Literal(f'This graph compares the ontologies {ont1} and {ont2}')))
        # Description
        graph.add((graph_ontology,
            rdflib.term.URIRef(NAMESPACES['dc']+'description'),
            rdflib.term.Literal(f'This graph compares the ontologies {ont1} and {ont2}')))


def serialize_graph(g1_clean, g1_name, g2_clean, g2_name, sentences_graphs_path, result_graph, rg_name,
                    result_graph_path, format='turtle'):
    destination_result_graph = result_graph_path + rg_name
    destination_g1 = sentences_graphs_path + g1_name
    destination_g2 = sentences_graphs_path + g2_name
    print("-" * 150)  # #########################################################
    print("Serializing graphs...")
    result_graph.serialize(destination=destination_result_graph, format=format)
    g1_clean.serialize(destination=destination_g1, format=format)
    g2_clean.serialize(destination=destination_g2, format=format)
