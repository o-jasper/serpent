
import pydot
from random import random

import io
from python_2_3_compat import to_str, is_str

from LLL_parser import LLLWriter


themes = {'basic' :
           {'default'      : [('fontname', 'Arial')],
            'default_edge' : [],
            'body'         : [('shape', 'box')],
            'control'      : [],
            'body_edge'    : [('penwidth', '2.0')],
            'true'         : [('label','true')],
            'false'        : [('label','false')],
            'plain_edge'   : [],
            'for_edge'     : [('label','loop'), ('back_too', 'plain_edge')],
#('dir','both')],
            'lll'          : [('label','lll')],
            'comment'      : [],
            'debug'        : [('label','bugifshown')]}}

class GraphCode:
    
    def __init__(self, graph=None, fr=None, uniqify=True, theme='basic', attrs=None,
                 write_fun=None, lllwriter=LLLWriter()):
        self.graph = graph or pydot.Dot('from-tree', graph_type='digraph')
        self.fr = fr
        self.uniqify = uniqify
        self.subnodes = {'lll':"_lll_", 'comment':""}

        self.attrs = attrs or themes[theme]
        self.calculated_attrs = {}
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
                return '()', []

            if is_str(ast[0]) and str(ast[0].lower()) in self.subnodes:
                name = ast[0].lower()
                use_str = self.subnodes[name]
                return use_str, [[name] + ast[1:]]
            else:
                ret_alt, ret_llls = [], []
                for el in ast:
                    alt, llls = self.control_flow_fix(el)
                    if alt not in ['seq', '']:
                        ret_alt.append(alt)
                    ret_llls = ret_llls + llls
                if len(ret_alt) == 0:
                    ret_alt = ['_seq_']
                return ret_alt, ret_llls
        else:
            return ast, []


    def get_attrs(self, of):
        if of not in self.attrs:
            return self.atts['default']
        elif of in self.calculated_attrs:
            return dict(self.calculated_attrs[of])
        else:
            val = dict(self.attrs[of])
            for sub in (val['derive'] if 'derive' in val else []) + ['default']:
                for el in self.attrs[sub]:
                    if el[0] not in val:
                        val[el[0]] = el[1]
            self.calculated_attrs[of] = val
            return dict(val)


    def add_node(self, added, which='default', uniqify=None):
        if uniqify is None:
            uniqify = self.uniqify

        if is_str(added):
            self.i += 1
            node = pydot.Node(str(self.i) if uniqify else added)
            node.obj_dict['attributes'] = self.get_attrs(which)
            node.set_label(added)
            added = node

        self.graph.add_node(added)
        return added


    def add_edge(self, fr, to, edge_which='default_edge'):
        edge = pydot.Edge(fr, to)
        attrs = self.get_attrs(edge_which)
        edge.obj_dict['attributes'] = attrs
        self.graph.add_edge(edge)
        if 'back_too' in attrs:  # Option to make a backward edge.
            back = pydot.Edge(to, fr)
            back.obj_dict['attributes'] = self.get_attrs(attrs['back_too'])
            self.graph.add_edge(back)


    def cf_add_node(self, added, fr, which, edge_which):
        llls = []
        if type(added) is list:
            added, llls = self.control_flow_fix(added)
            added = self.cf_expr_str(added)

        added = self.add_node(added, which)

        if fr is not None:
            self.add_edge(fr, added, edge_which)

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

# Note: all the 'straight graph' stuff is a slap-on.
    def sg_add_node(self, added, fr=None, uniqify=None):
        node = self.add_node(added, uniqify=uniqify)
        if fr is not None:
            self.add_edge(fr, node)
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
