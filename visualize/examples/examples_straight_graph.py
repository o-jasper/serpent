import os.path
import sys

fromdir = os.path.dirname(__file__)
sys.path.append(os.path.join(fromdir, '..'))
sys.path.append(os.path.join(fromdir, '../../serpent/'))

import io

from visualize import straight_graph
from LLL_parser import LLLParser


def straight_graph_file(file, graph=None, fr=None):

    with open(file, 'r') as stream:
        tree = LLLParser().parse_lll_stream(stream)

    return straight_graph(tree)


def sg_f(el):
    g = straight_graph_file(fromdir + '/' + el + '.lsp')
    to = str(fromdir) + '/sg_' + el[-4:] + '.svg'
    print(to)
    g.write(to, format = 'svg')

sg_f('SubCurrency')

for el in ['Bank', 'kv', 'NameReg', 'Splitter', 'SubCurrency']:
    sg_f(el)
