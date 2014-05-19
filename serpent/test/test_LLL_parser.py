import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from LLL_parser import LLLParser

print(LLLParser().parse_lll('q(a b [a] 3 [ [b]] 432)'))
