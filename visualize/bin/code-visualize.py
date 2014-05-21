#!/usr/bin/python2

import os.path
import sys

fromdir = os.path.dirname(__file__)
sys.path.append(os.path.join(fromdir, '..'))
sys.path.append(os.path.join(fromdir, '../../serpent/'))

import argparse

parser = argparse.ArgumentParser(description="""Visualize code with graphviz.
Control flow available.""")
parser.add_argument('input',  help='Input LLL file.')
parser.add_argument('output', help='Output file.')
parser.add_argument('--prog', default='dot',
                    help='Graphviz program to use dot|twopi|neato|circo|fdp.')
parser.add_argument('--format', default=None,
                    help='Output format, defaults based on output file.')
parser.add_argument('--which', default='cf',
                    help='What kind, sg|cf for straight graph/control flow.')
parser.add_argument('--comments', default='no',
                    help='Link comments aswel')
args = parser.parse_args()

from visualize import GraphCode
from LLL_parser import LLLParser


def graph_file(which, fr, to, prog='dot', format=None, comment_name=None):
    gc = GraphCode()
    tree = LLLParser(comment_name=comment_name).parse_lll_file(fr)
    if which in ['sg']:
        g = gc.straight(['root'] + tree)
    elif which in ['cf']:
        g = gc.control_flow(tree)

    if format is None:
        format = to[-3:]
    g.write(to, format=format, prog=prog)

graph_file(args.which, args.input, args.output, args.prog,
           args.format, 'comment' if args.comments == 'yes' else None)
