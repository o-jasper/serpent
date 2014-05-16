
#from s_expr_parser import SExprParser

import pydot
from random import random


def assert_len(ast, length, say="wrong_length, should be"):
    if len(ast) != length:
        raise Exception(say, length, len(ast), ast)

# Graph straight from tree.
def straight_graph(tree, graph=None, fr=None):
    if graph is None:  # Otherwise graph is in-effect a global object.
        graph = pydot.Dot('from-tree', graph_type='digraph')

    def sg(el, fr):
        straight_graph(el, graph, fr)

    def an(added):
        graph.add_node(pydot.Node(added))
        if fr is not None:
            graph.add_edge(pydot.Edge(fr, added))

    if type(tree) is list:
        if len(tree) > 0:
            if type(tree[0]) != str:
                raise Exception('First argument not name', tree)
            an(tree[0])
    
            for el in tree[1:]:
                sg(el, tree[0])
        else:
            an('()')
    else:
        an(tree)
    return graph
