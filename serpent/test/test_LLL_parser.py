import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from LLL_parser import LLLParser

print(LLLParser().parse_lll('q(a b [a] 3 [ [b]] 432)'))

print(LLLParser().parse_lll('a "string" b'))

print(LLLParser().parse_lll('@@a @@ b @@(calldataload 0) @@ (calldataload 0)'))


print(LLLParser().parse_lll(""" {
  [0] "Bank"
  (call 0x929b11b8eeea00966e873a241d4b67f7540d1f38 0 0 0 4 0 0)
  }"""))
