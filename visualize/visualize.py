
import pydot
from random import random

import io

# Python 2 wants unicode..
#(from s_expr_parser import s_expr_str)
def s_expr_write(stream, input, o='(', c=')', w=' '):
    def handle_1(el):
        if type(el) is list:
            stream.write(unicode(o))
            s_expr_write(stream, el, o=o, c=c, w=w)
            stream.write(unicode(c))
        else:
            stream.write(unicode(el))

    if len(input) > 0:
        handle_1(input[0])
        for el in input[1:]:
            stream.write(unicode(w))
            handle_1(unicode(el))


def s_expr_str(tree, o='(', c=')', w=' '):
    stream = io.StringIO()
    s_expr_write(stream, tree, o=o, c=c, w=w)
    stream.seek(0)  # Dont forget to read back!
    return stream.read()



# Graph control flow.
def control_flow_graph(ast, graph=None, fr=None):
    
    if graph is None:
        graph = pydot.Dot('from-tree', graph_type='digraph')


    def an(added):
        if type(added) is list:
            added = s_expr_str(added)
        if type(added) in [list, unicode]:
            added = pydot.Node(added)

        graph.add_node(added)
        if fr is not None:
            graph.add_edge(pydot.Edge(fr, added))
        return added

    def cfg(el):
        control_flow_graph(el, graph, fr)

    i, j = 0, 0
    while i < len(ast):
            
        el = ast[i]
        if type(el) is list:
            assert len(el) > 0

            pre_n = {'when' : 2, 'unless' : 2, 'for' : 4, 'seq' : 1, 'if' : None}
            if el[0] in pre_n:
                if i-1 > j:  # Collect stuff in between.
                    fr = an(ast[j:i-1])
                j = i + 1
                
                if el[0] == 'if':
                    assert len(el) in [3,4]
                    fr = an(el[2:]) # The condition.
                    cfg(el[2])
                    if len(el) == 4:
                        cfg(el[3])
                else:
                    n = pre_n[el[0]]
                    if len(el) < n:
                        raise Exception('Not enough arguments', len(el), el)

                    fr= an(el[:n])
                    cfg(el[n:])
        i += 1
    if i != j:
        an(ast[i:])
    return graph

# Graph straight from tree.
def straight_graph(tree, graph=None, fr=None, uniqify=False, store = None):
    # NOTE: cant set in arguments, would effectively be global variable!
    if uniqify and store is None:  # Store is for 
        store = {}
    if graph is None:
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
