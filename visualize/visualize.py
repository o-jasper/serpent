
import pydot
from random import random

import io
from python_2_3_compat import to_str, is_str

from s_expr_parser import s_expr_write


def cf_expr_str(seq):
    if not (type(seq) is list and len(seq) > 0):
        raise Exception(seq)
    stream = io.StringIO()
    s_expr_write(stream, seq[0])
    for el in seq[1:]:
        stream.write(to_str('\n'))
        s_expr_write(stream, el)
    stream.seek(0)  # Dont forget to read back!
    return stream.read()


themes = {'basic' : {'body'     : [('shape', 'box')],
                     'control'  : [],
                     'body_edge': [],
                     'true'     : [('label','true')],
                     'false'    : [('label','false')],
                     'loop'     : [('label','loop')],
                     'lll'      : [('label','lll')],
                      'comment'  : []} }

class GraphCode:

    def __init__(self, graph=None, fr=None, uniqify=False, theme='basic', attrs=None):
        if graph is None:
            self.graph = pydot.Dot('from-tree', graph_type='digraph')
        else:
            self.graph = graph
        self.fr = fr
        self.uniqify = uniqify
        self.cnt = {'lll':0, 'comment':0}

        if attrs is None:
            attrs = themes[theme]
        self.attrs = attrs


    # Takes everything out that isnt 
    def control_flow_fix(self, ast):
        if type(ast) == list:
            if len(ast) == 0:
                return 'empty_list', []

            if is_str(ast[0]) and str(ast[0]) in self.cnt:
                self.cnt[ast[0]] += 1
                repr_str = '<' + ast[0] + '_' + str(self.cnt[ast[0]]) + '>'
                return repr_str, [[repr_str] + ast[1:]]
            else:
                ret_alt, ret_llls = [], []
                for el in ast:
                    alt, llls = self.control_flow_fix(el)
                    if alt != 'seq':
                        ret_alt.append(alt)
                    ret_llls = ret_llls + llls
                if len(ret_alt) == 0:
                    ret_alt = ['<seq>']
                return ret_alt, ret_llls
        else:
            return ast, []


    def cf_add_node(self, added, fr, which, edge_which):
        llls = []
        if type(added) is list:
            added, llls = self.control_flow_fix(added)
            added = cf_expr_str(added)
        if is_str(added):
            added = pydot.Node(added)
        if which in self.attrs:
            added.obj_dict['attributes'] = dict(self.attrs[which])

        self.graph.add_node(added)
        if fr is not None:
            edge = pydot.Edge(fr, added)
            if type(edge_which) is list:
                edge.obj_dict['attributes'] = dict(edge_which)
            else:
                edge.obj_dict['attributes'] = dict(self.attrs[edge_which])
            self.graph.add_edge(edge)

        for lll in llls:
            self.control_flow(lll[1:], added, [('label',lll[0])])
        return added


    def control_flow(self, ast, fr=None, fr_which='body_edge'):
        assert type(ast) is list

        if fr is None:
            fr = self.fr
    
        i, j = 0, 0
        while i < len(ast):
    
            el = ast[i]
            if type(el) is list:
                if len(el) == 0:
                    raise Exception('Zero length entry?', i, ast)
    
                pre_n = {'when' : (2, 'true'), 'unless' : (2, 'false'),
                          'for' : (4, 'loop'), 'seq' : (1,None),
                          'lll' : (1, 'lll'), 'if' : (None,None)}
                if el[0] in pre_n:
                    if j < i-1:  # Collect stuff in between.
                        fr = self.cf_add_node(ast[j:i-1], fr, 'body', fr_which)
                        fr_which = 'body_edge'
                    j = i + 1

                    if el[0] == 'if':
                        assert len(el) in [3,4]
                        fr = self.cf_add_node(el[:2], fr, 'control', fr_which) # The condition.
                        self.control_flow([el[2]], fr, 'true')
                        if len(el) == 4:
                            self.control_flow([el[3]], fr, 'false')
                    else:
                        n, which = pre_n[el[0]]
                        if len(el) < n:
                            raise Exception('Not enough arguments', len(el), el)

                        if el[0] not in ['seq']:
                            fr = self.cf_add_node(el[:n], fr, 'control', fr_which)
                        else:
                            which = fr_which
                        self.control_flow(el[n:], fr, which)
            i += 1
        if j < i:
            self.cf_add_node(ast[j:], fr, 'body', fr_which)
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
