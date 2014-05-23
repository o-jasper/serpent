
import pydot
from random import random

import io
from python_2_3_compat import to_str, is_str

from LLL_parser import LLLWriter


themes = {'basic' : {'body'     : [('shape', 'box')],
                     'control'  : [],
                     'body_edge': [('penwidth', '2.0')],
                     'true'     : [('label','true')],
                     'false'    : [('label','false')],
                     'for_edge' : [('label','loop'), ('dir','both')],
                     'lll'      : [('label','lll')],
                     'comment'  : [],
                     'debug'    : [('label','bugifshown')]}}

class GraphCode:
    
    def __init__(self, graph=None, fr=None, uniqify=False, theme='basic', attrs=None,
                 write_fun=None, lllwriter=LLLWriter()):
        self.graph = graph or pydot.Dot('from-tree', graph_type='digraph')
        self.fr = fr
        self.uniqify = uniqify
        self.subnodes = {'lll':(False, "<lll>"), 'comment':(False, "")}

        self.attrs = attrs or themes[theme]
        self.write_fun = write_fun or lllwriter.write_lll_stream
        
        self.i = 0

    def cf_expr_str(self, seq):
        if not (type(seq) is list and len(seq) > 0):
            raise Exception(seq)
        stream = io.StringIO()
        self.write_fun(stream, seq[0])
        for el in seq[1:]:  # Here for the newlines.
            stream.write(to_str('\n'))
            self.write_fun(stream, el)
        stream.seek(0)  # Dont forget to read back!
        return stream.read()


    # Checks if parts of expressions need more nodes.
    def control_flow_fix(self, ast):
        if type(ast) == list:
            if len(ast) == 0:
                return 'empty_list', []

            if is_str(ast[0]) and str(ast[0].lower()) in self.subnodes:
                name = ast[0].lower()
                use_pattern, pattern = self.subnodes[name]
                if use_pattern:
                    repr_str = pattern % name
                    return repr_str, [[name] + ast[1:]]
                else:
                    return '', [[name] + ast[1:]]
            else:
                ret_alt, ret_llls = [], []
                for el in ast:
                    alt, llls = self.control_flow_fix(el)
                    if alt not in ['seq', '']:
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
            added = self.cf_expr_str(added)
        if is_str(added):
            self.i += 1
            node = pydot.Node(str(self.i))
            if which in self.attrs:
                node.obj_dict['attributes'] = dict(self.attrs[which])
            node.set_label(added)
            added = node

        self.graph.add_node(added)
        if fr is not None:
            edge = pydot.Edge(fr, added)
            if type(edge_which) is list:
                edge.obj_dict['attributes'] = dict(edge_which)
            else:
                edge.obj_dict['attributes'] = dict(self.attrs[edge_which])
            self.graph.add_edge(edge)

        for lll in llls:
            self.control_flow([lll[1]], added, lll[0]) #'lll')
        return added


    def control_flow(self, ast, fr=None, fr_which='body_edge'):
        assert type(ast) is list

        fr = fr or self.fr
    
        i, j = 0, 0
        while i < len(ast):
    
            el = ast[i]
            if type(el) is list:
                if len(el) == 0:
                    raise Exception('Zero length entry?', i, ast)
    
                pre_n = {'when' : (2, 'true'), 'unless' : (2, 'false'),
                          'for' : (4, 'for_edge'), 'seq' : (1,None),
                          'lll' : (1, 'lll'), 'if' : (None,None)}
                name = el[0].lower()
                if name in pre_n:
                    if j < i-1:  # Collect stuff in between.
                        fr = self.cf_add_node(ast[j:i-1], fr, 'body', fr_which)
                        fr_which = 'body_edge'
                    j = i + 1

                    if name == 'if':
                        assert len(el) in [3,4]  # The condition.
                        fr = self.cf_add_node(el[:2], fr, 'control', fr_which)
                        self.control_flow([el[2]], fr, 'true')
                        if len(el) == 4:
                            self.control_flow([el[3]], fr, 'false')
                    else:
                        n, which = pre_n[name]
                        if len(el) < n:
                            raise Exception('Not enough arguments', len(el), el)

                        if name not in ['seq']:
                            fr = self.cf_add_node(el[:n], fr, 'control', fr_which)
                        else:
                            which = fr_which
                        self.control_flow(el[n:], fr, which)
                    fr_which = 'body_edge'
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
        fr = fr or self.fr

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
