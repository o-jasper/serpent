
#from s_expr_parser import SExprParser

import pydot
from random import random


def gen_tree(p, n, d):
    out = [str(random())]
    for i in range(n):
        if random() < p and d > 0:
            out.append(gen_tree(p, n, d - 1))
        else:
            out.append(str(random()))
    return out


def assert_len(ast, length, say="wrong_length, should be"):
    if len(ast) != length:
        raise Exception(say, length, len(ast), ast)

# Graph straight from tree.
def straight_graph(tree, graph=None, fr=None):
    if graph is None:  # Otherwise graph is in-effect a global object.
        graph = pydot.Dot('from-tree', graph_type='digraph')

    if fr is None:
        graph.add_node(pydot.Node('root'))
        fr = 'root'

    def sg(el, fr):
        straight_graph(el, graph, fr)

    def an(added):
        graph.add_node(pydot.Node(added))
        graph.add_edge(pydot.Edge(fr, added))

    if type(tree) is list:
        assert len(tree) > 0 and type(tree[0]) == str
        an(tree[0])

        for el in tree[1:]:
            sg(el, tree[0])
    else:
        an(tree)
    return graph


g = straight_graph(gen_tree(0.2, 2, 2))

g.write('sg.svg', format='svg')
