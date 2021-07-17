import constants
import spacy
from rdflib.term import Literal
from nltk.corpus import wordnet

nlp_analyzer = spacy.load('en_core_web_sm')
n = 0

def pad_prefix(el, graph):
    return "{:<50}".format(el.n3(graph.namespace_manager))


def prefix(el, graph):
    return pad_prefix(el, graph).strip()


def word(el, graph):
    return prefix(el, graph).split(":")[1].lower().translate({ord(x): '' for x in "_1234567890"})


def index_generator():
    num = 1
    while True:
        yield str(num)
        num += 1


# return all the synonyms of all the possible meanings of word (return a list of strings)
def get_word_synonyms(word):
    return [str(lemma.name()) for syn_set in wordnet.synsets(word) for lemma in syn_set.lemmas()]


def lemma(text):
    if isinstance(text, Literal):
        text = str(text)
    return " ".join([token.lemma_ for token in nlp_analyzer(text)])


def is_class(obj, graph):
    is_explicit_class = graph.value(subject=obj, predicate=constants.TYPE_PREDICATE, default=None) == constants.CLASS_OBJECT
    is_subclass_of = graph.value(subject=obj, predicate=constants.SUBCLASS_PREDICATE, default=None) is not None
    is_type_of = graph.value(object=obj, predicate=constants.TYPE_PREDICATE, default=None) is not None
    return is_explicit_class or is_subclass_of or is_type_of


def get_node_triples(node, g):
    result = []
    for s, p, o in g:
        if (s == node or o == node) and p != constants.LABEL_PREDICATE:
            result.append((s, p, o))
    return result

def superclasses(node, g):
    unwanted_superclasses = ['dul:Event', 'owl:Class']

    classes = list(g.objects(node, constants.TYPE_PREDICATE))
    still_classes = classes != []
    while(still_classes):
        before = len(classes)
        to_add = list(g.objects(classes[-1], constants.SUBCLASS_PREDICATE))
        classes = classes + to_add
        after = len(classes)
        if(after == before):
            still_classes = False
        #print([prefix(c, g) for c in classes])
    classes = filter(lambda x: len(list(g.subjects(constants.TYPE_PREDICATE, x)))<2, classes)
    return list(filter(lambda x: prefix(x,g) not in unwanted_superclasses, classes))

