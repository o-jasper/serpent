import os.path
import sys

fromdir = os.path.dirname(__file__)
sys.path.append(os.path.join(fromdir, '..'))
sys.path.append(os.path.join(fromdir, '../../serpent/'))

import io

from visualize import control_flow_graph
from LLL_parser import LLLParser


def control_flow_graph_file(file, graph=None, fr=None):

    with open(file, 'r') as stream:
        tree = LLLParser().parse_lll_stream(stream)

    return control_flow_graph(tree)


# {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}

def sg_f(el):
    fn = (str(fromdir) + '/' if str(fromdir) != '' else '')
    g = control_flow_graph_file(fn + el + '.lsp')
    to = fn + 'cf_' + el + '.svg'
    print(to)
    g.write(to, format = 'svg', prog='dot')

sg_f('SubCurrency')

for el in ['Bank', 'kv', 'NameReg', 'Splitter', 'SubCurrency']:
    sg_f(el)
