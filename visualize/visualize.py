
import pydot
from random import random


def assert_len(ast, length, say="wrong_length, should be"):
    if len(ast) != length:
        raise Exception(say, length, len(ast), ast)

# Graph straight from tree.
def straight_graph(tree, graph=None, fr=None, uniqify=False, store = None):
    if uniqify and store is None:
        store = {}
    if graph is None:  # Otherwise graph is in-effect a global object.
        graph = pydot.Dot('from-tree', graph_type='digraph')

    def sg(el, fr):
        straight_graph(el, graph, fr, uniqify, store)

    def an(added):
     # TODO bleh how do you get them unique.. Why isnt it unique by default?!
        if uniqify:
            while added in store:
                added = '.' + added
            store[added] = True
        
        node = pydot.Node(added)
        graph.add_node(node)
        if fr is not None:
            graph.add_edge(pydot.Edge(fr, node))
        return node

    if type(tree) is list:
        if len(tree) > 0:
            if type(tree[0]) != str:
                raise Exception('First argument not name', tree)
            root = an(tree[0])
    
            for el in tree[1:]:
                sg(el, root)
        else:
            an('()')
    else:
        an(tree)
    return graph
