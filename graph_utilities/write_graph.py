import rdflib
from utilities.utility_functions import pad_prefix
from utilities import constants

def complete_graph(g1, g2, result_graph):
    ps = [constants.TYPE_PREDICATE, constants.SUBCLASS_PREDICATE]
    # Add type information for graph g1
    for s in result_graph.subjects():
        for p in ps:
            os = list(g1.objects(subject=s, predicate=p))
            for o in os:
                result_graph.add((s,p,o))
                #print(pad_prefix(s, result_graph), pad_prefix(p, result_graph), pad_prefix(o, result_graph))
    # Add type information for graph g2
    for s in result_graph.objects():
        for p in ps:
            os = list(g2.objects(subject=s, predicate=p))
            for o in os:
                result_graph.add((s,p,o))
                #print(pad_prefix(s, result_graph), pad_prefix(p, result_graph), pad_prefix(o, result_graph))

    for p in result_graph.predicates():
        result_graph.add((p, constants.TYPE_PREDICATE, rdflib.OWL.ObjectProperty))


def write_graph(g1, g2, result_graph, destination='results/output.ttl', format='turtle'):
    # Write graph to file
    print("WRITING")
    complete_graph(g1, g2, result_graph)
    result_graph.serialize(destination=destination, format=format)