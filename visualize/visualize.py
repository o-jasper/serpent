
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
            handle_1(el)


def cf_expr_str(seq):
    assert len(seq) > 0
    stream = io.StringIO()
    s_expr_write(stream, seq[0])
    for el in seq[1:]:
        stream.write(unicode('\n'))
        s_expr_write(stream, el)
    stream.seek(0)  # Dont forget to read back!
    return stream.read()


class GraphCode:

    def __init__(self, graph=None, fr=None, uniqify=False):
        if graph is None:
            self.graph = pydot.Dot('from-tree', graph_type='digraph')
        else:
            self.graph = graph
        self.fr = fr
        self.uniqify = uniqify
        self.lll_cnt = 0


    # Takes everything out that isnt 
    def control_flow_fix(self, ast):
        if type(ast) == list:
            if len(ast) == 0:
                return 'empty_list', []
                
            if ast[0] == 'lll':  # Only thing that can cause a need for graphing insides!
                self.lll_cnt += 1
                return 'lll(' + str(self.lll_cnt) + ')', [ast]
            else:
                ret_alt, ret_llls = [], []
                for el in ast:
                    alt, llls = self.control_flow_fix(el)
                    ret_alt.append(alt)
                    ret_llls = ret_llls + llls
                return ret_alt, ret_llls
        else:
            return ast, []


    def cf_add_node(self, added, fr):
        llls = []
        if type(added) is list:
            added, llls = self.control_flow_fix(added)
            added = cf_expr_str(added)
        if type(added) in [list, unicode]:
            added = pydot.Node(added)

        self.graph.add_node(added)
        if fr is not None:
            self.graph.add_edge(pydot.Edge(fr, added))

        for lll in llls:
            self.control_flow(lll[1:], fr=added)
        return added


    def control_flow(self, ast, fr=None):
        assert type(ast) is list

        if fr is None:
            fr = self.fr
    
        i, j = 0, 0
        while i < len(ast):
    
            el = ast[i]
            if type(el) is list:
                if len(el) == 0:
                    raise Exception('Zero length entry?', i, ast)
    
                pre_n = {'when' : 2, 'unless' : 2, 'for' : 4, 'seq' : 1,
                          'lll' : 1, 'if' : None}
                fixed = []
                if el[0] in pre_n:
                    if j < i-1:  # Collect stuff in between.
                        fr = self.cf_add_node(ast[j:i], fr)
                        j = i + 1
                    if el[0] == 'if':
                        assert len(el) in [3,4]
                        fr = self.cf_add_node(el[2], fr) # The condition.
                        self.control_flow(el[3], fr)
                        if len(el) == 4:
                            self.control_flow(el[3], fr)
                    else:
                        n = pre_n[el[0]]
                        if len(el) < n:
                            raise Exception('Not enough arguments', len(el), el)
    
                        fr= self.cf_add_node(el[:n], fr)
                        self.control_flow(el[n:], fr)
                    fixed.append('SHOULDNT APPEAR')

            i += 1
        if i != j:
            self.cf_add_node(ast[j:], fr)
        return self.graph


    def sg_add_node(self, added, fr):
       # TODO bleh how do you get them unique.. Why isnt it unique by default?!
        if self.uniqify:
            while added in store:
                added = '.' + added
                store[added] = True

        node = pydot.Node(added)
        self.graph.add_node(node)
        if fr is not None:
            self.graph.add_edge(pydot.Edge(fr, node))
        return node

    # Graph straight from tree.
    def straight(self, tree, fr=None):
        if fr is None:
            fr = self.fr

        if type(tree) is list:
            if len(tree) > 0:
                if type(tree[0]) != str:
                    raise Exception('First argument not name', tree)
                root = self.sg_add_node(tree[0], fr)
        
                for el in tree[1:]:
                    self.straight(el, root)
            else:
                self.sg_add_node('()', fr)
        else:
            self.sg_add_node(tree, fr)
        return self.graph
