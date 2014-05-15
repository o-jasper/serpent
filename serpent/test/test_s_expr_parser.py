
import os.path
import io
import sys
from random import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from s_expr_parser import SExprParser, s_expr_str


def gen_tree(p, n, d):
    out = []
    for i in range(n):
        if random() < p and d > 0:
            out.append(gen_tree(p, n, d - 1))
        else:
            out.append(str(random()))
    return out


class TestParser(SExprParser):

    # Class essentially just stops me from having to pass these all the time.
    # Just do SExprParser().parse(), dont neccesarily need a variable.
    def __init__(self, info=''):
        self.info = info
        self.start_end = [('(', ')',  True,  True,  None),
                          (';', '\n', False, False, 'scrub'),
                          ('"', '"',  True,  True,  'str')]
        self.wrong_end_warning = True
        self.white = [' ', '\t', ' ']
        self.earliest_macro = {}

    def test_case(self, string, tree, o='(', c=')', white=[' ', '\t', '\n']):
        result = self.parse(string)
        if result != tree:
            raise Exception(self.info,
                            'tree', tree, 'string', string, 'result', result)

    def test_1(self, p=0.1, n=2, d=2):
        tree = gen_tree(p, n, d)
        self.test_case(s_expr_str(tree), tree)


# Simple case test.
TestParser('simple_case').test_case("bla 123 (45(678      af)sa faf((a sf))  (a) sfsa) ;do not include",
                        ['bla', '123', ['45', ['678', 'af'],
                        'sa', 'faf', [['a', 'sf']], ['a'], 'sfsa']])

# IMO Should have been caught in a test and not ended up downstream.
for i in range(200):
    TestParser("autocase:%d"%i).test_1()

# Thought it was a python bug somehow.. where are those zeros coming from...
for i in range(200):
    x = random()
    s=io.StringIO("")
    s.write(str(x))
    s.seek(0)
    got = s.read()
    if got != str(x):
        raise Exception('python bug!?', got, str(x), x)
