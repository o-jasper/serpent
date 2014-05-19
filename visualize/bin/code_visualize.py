#!/usr/bin/python2

import os.path
import sys

fromdir = os.path.dirname(__file__)
sys.path.append(os.path.join(fromdir, '..'))
sys.path.append(os.path.join(fromdir, '../../serpent/'))

import io

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("which",  help="What kind, sg|cf for straight graph/control flow.")
parser.add_argument("input",  help="Input LLL file.")
parser.add_argument("output", help="Output file, type implied.")
args = parser.parse_args()

from visualize import GraphCode
from LLL_parser import LLLParser


def get_tree(file):
    with open(file, 'r') as stream:
        tree = LLLParser().parse_lll_stream(stream)
    return tree


# {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}

def sg_f(which, fr, to):
    fn = (str(fromdir) + '/' if str(fromdir) != '' else '')
    gc = GraphCode()
    if which in ['sg']:
        g = gc.straight(['root'] + get_tree(fr))
    elif which in ['cf']:
        g = gc.control_flow(get_tree(fr))

    g.write(to, format = to[-3:], prog='dot')

sg_f(args.which, args.input, args.output)
