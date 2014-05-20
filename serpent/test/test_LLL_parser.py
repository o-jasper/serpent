import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from LLL_parser import LLLParser, LLLWriter


def case(input):
    tree = LLLParser().parse_lll(input)
    string = LLLWriter().write_lll(tree)
    print(string)
    tree_after = LLLParser().parse_lll(string)[0]
    if tree != tree_after:
        raise Exception('mismatch before/after', tree, tree_after)

case('q(a b [a] 3 [ [b]] 432)')

case('a "string" b')

case('@@a @@ b @@(calldataload 0) @@ (calldataload 1)')

case(""" {
  [0] "Bank"
  (call 0x929b11b8eeea00966e873a241d4b67f7540d1f38 0 0 0 4 0 0)
  }""")
