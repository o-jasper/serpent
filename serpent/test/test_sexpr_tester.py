
import os.path
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
    def __init__(self):
        self.start_end = [('(', ')',  True,  True,  None),
                          (';', '\n', False, False, 'scrub'),
                          ('"', '"',  True,  True,  'str')]
        self.wrong_end_warning = True
        self.white = [' ', '\t', ' ']
        self.earliest_macro = {}

    def test_case(self, string, tree, o='(', c=')', white=[' ', '\t', '\n']):
        result = self.parse(string)
        if result != tree:
            print('tree:  ', tree)
            print('string:', string)
            print('result:', result)

        assert result == tree

    def test_1(self, p=0.1, n=2, d=2):
        tree = gen_tree(p, n, d)
        self.test_case(s_expr_str(tree), tree)


# Simple case test.
TestParser().test_case("bla 123 (45(678      af)sa faf((a sf))  (a) sfsa) ;do not include",
                       ['bla', '123', ['45', ['678', 'af'],
                        'sa', 'faf', [['a', 'sf']], ['a'], 'sfsa']])

# This test fails! Its a Python bug!
# x=io.StringIO("")
# x.write("00.4528490737968983")
# x.seek(0)
# x.read() # -> '00.4528490737968983' !!!
#
# IMO Should have been caught in a test and not ended up downstream.
for el in range(200):
    TestParser().test_1()
