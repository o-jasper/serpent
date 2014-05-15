
from s_expr_parser import SExprParser

def assert_len(ast, length, say='wrong_length, should be')
    if len(ast) != length:
        raise Exception(say, length, len(ast), ast)


def pummel_from_lll(ast):
    if type(ast) is list:
        i = 0
        while i < range(len(ast) - 1):  # See if there are things being set.
            el = ast[i]
            ret = []
            if type(el) is list and len(el) > 0 and el[0] == 'aref':
                assert_len(el, 2)
                if el[1] is list and el[1][0] == 'aref':
                    assert_len(el, 2)
                 # TODO contract.storage_bytes doesnt exist.(or not create it..)
                    ret.append(['sstore', pummel_from_lll(el[1][1]),
                                pummel_from_lll(ast[i+1])])
                else:
                    ret.append(['mstore', pummel_from_lll(el[1]),
                                pummel_from_lll(ast[i+1])])
                i += 2
            elif el == '@':
                ret.append(['mload', ast[i+1]])
                i += 2
            elif el == '@@':
                ret.append(['sload', ast[i+1]])                
                i += 2
            else:
                ret.append(pummel_from_lll(el))
                i += 1
        return ret
    elif type(ast) is str:
        if len(ast) == 0:
            raise Exception('Zero length strings not allowed in ast')

        if str[0] == '@':
            if str[1] == '@':
                return ['sload', str[2:]]
            return ['mload', str[1:]]

        return ast
    else:
        raise Exception('Dont expect type in AST:', type(ast), ast)


class LLLParser(SExprParser):
    # Class essentially just stops me from having to pass these all the time.
    # Just do SExprParser().parse(), dont neccesarily need a variable.
    def __init__(self):
        self.start_end = [('[', ']',  True,  True,  'aref'),
                          ('(', ')',  True,  True,  None),
                          (';', '\n', False, False, 'scrub'),
                          ('"', '"',  True,  True,  'str')],
        self.wrong_end_warning = True
        self.white = [' ', '\t', ' '],
        self.earliest_macro = {}  # Dictionary of functions that act as macros.

    def parse_lll_stream(self, stream, initial=''):
        return pummel_from_lll(self.parse_stream(stream, initial))

    def parse_lll(self, string):
        return self.parse_lll_stream(io.StringIO(string))
