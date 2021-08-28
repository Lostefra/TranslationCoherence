import rdflib
from rdflib.term import URIRef
from utilities.utility_functions import prefix
from utilities import constants

def has_equivalent(node, graph):
	equivalents = list(graph.subjects(predicate=constants.EQUIVALENCE_PREDICATE, object=node)) + \
	              list(graph.subjects(predicate=constants.SYNONYMY_PREDICATE, object=node)) + \
	              list(graph.objects(subject=node, predicate=constants.EQUIVALENCE_PREDICATE)) + \
	              list(graph.objects(subject=node, predicate=constants.SYNONYMY_PREDICATE))
	if equivalents:
		return True
	return False


# def multiple_classified(node1, node2, n, result_graph):
# 	expressions = result_graph.subject_objects(predicate=n.differentExpression)
# 	exprs_1, exprs_2 = [], []
# 	list_exprs = list(map(list, zip(*expressions)))
# 	if list_exprs:
# 		exprs_1, exprs_2 = list_exprs[0], list_exprs[1]
# 		# print(f"{exprs_1}, {exprs_2}")
# 		return any([(expr_1, n.involves_node, node1) in result_graph for expr_1 in exprs_1 + exprs_2]) or \
# 			any([(expr_2, n.involves_node, node2) in result_graph for expr_2 in exprs_2 + exprs_1])
# 	return False


def check_multiples(g1, g2, n, result_graph, indexes, lemmas, frontiers, new_frontiers):
	# Check for pattern "several"

	# fred:number_1 fred:numberOf | bunchOf | seriesOf, quant:hasQuantifier quant:multiple | quant:some, hasQuality fred:Several

	multiples = ['number', 'bunch', 'series', 'array', 'collection', 'group', 'amount']
	quantifiers = ['multiple', 'some', 'many']
	quant_predicate = URIRef(constants.NAMESPACES['quant'] + 'hasQuantifier')

	for node1, node2 in frontiers:
		objs = list(g2.objects(subject=node2, predicate=quant_predicate))
		if any([q in obj for q in quantifiers for obj in objs]):# and not multiple_classified(node1, node2, n, result_graph):
			# print(f"OBJS: {[prefix(o2, g2) for o2 in objs]}")
			for s1, p1 in g1.subject_predicates(object=node1):
				if not has_equivalent(s1, result_graph):
					for m in multiples:
						if m in prefix(p1, g1):# and any([q in prefix(o2,g2) for q in quantifiers for o2 in objs]):
							# Create a hierarchy relationship
							# "multiples_i" is a reification of a N-ary relationship
							expr_1 = "expression_" + next(indexes["expressions"])
							expr_2 = "expression_" + next(indexes["expressions"])
							result_graph.add((n[expr_1], constants.TYPE_PREDICATE,
											  rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))
							result_graph.add((n[expr_2], constants.TYPE_PREDICATE,
											  rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))
							result_graph.add((n[expr_1], n.involvesNoun, node1))
							result_graph.add((n[expr_1], n.involvesMultiple, s1))
							result_graph.add((n[expr_2], n.involvesNoun, node2))
							for obj in objs:
								result_graph.add((n[expr_2], quant_predicate, obj))
								result_graph.add((n[expr_1], n.differentExpression, n[expr_2]))
							# print("FOUND", prefix(node1, g1), prefix(p1, g1), prefix(node2, g2), [prefix(o2, g2) for o2 in objs])

		objs = list(g1.objects(subject=node1, predicate=quant_predicate))
		if any([q in obj for q in quantifiers for obj in objs]):# and not multiple_classified(node1, node2, n, result_graph):
			# print(f"OBJS: {[prefix(o1, g1) for o1 in objs]}")
			for s2,p2 in g2.subject_predicates(object=node2):
				if not has_equivalent(s2, result_graph):
					for m in multiples:
						if m in prefix(p2, g2):# and any([q in prefix(o1,g1) for q in quantifiers for o1 in objs]):
							# Create a hierarchy relationship
							# "multiples_i" is a reification of a N-ary relationship
							expr_1 = "expression_" + next(indexes["expressions"])
							expr_2 = "expression_" + next(indexes["expressions"])
							result_graph.add((n[expr_1], constants.TYPE_PREDICATE,
											  rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))
							result_graph.add((n[expr_2], constants.TYPE_PREDICATE,
											  rdflib.term.URIRef(constants.NAMESPACES["translation_coherence_vocabulary"] + "Expression")))
							result_graph.add((n[expr_1], n.involvesNoun, node1))
							for obj in objs:
								result_graph.add((n[expr_1], quant_predicate, obj))
							result_graph.add((n[expr_2], n.involvesNoun, node2))
							result_graph.add((n[expr_2], n.involvesMultiple, s2))
							result_graph.add((n[expr_1], n.differentExpression, n[expr_2]))
							# print("FOUND", prefix(node2, g2), prefix(p2, g2), prefix(node1, g1), [prefix(o1, g1) for o1 in objs])
