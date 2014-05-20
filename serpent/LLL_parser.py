
import io
from python_2_3_compat import to_str, is_str
from s_expr_parser import SExprParser


def assert_len(ast, length, say="wrong_length, should be"):
    if len(ast) != length:
        raise Exception(say, length, len(ast), ast)


# Assumes `sstore`, `mstore`, `sload`, `mload`, will do vars.
def lll_to_s_expr(ast):
    if type(ast) is list:
        i = 0
        ret = []
        while i < len(ast) - 1:  # See if there are things being set.
            el = ast[i]
            if type(el) is list and len(el) > 0 and el[0] == 'aref':
                assert_len(el, 2)
                if type(el[1]) is list and el[1][0] == 'aref':
                    assert_len(el, 2)
                # TODO contract.storage_bytes doesnt exist.(or not create it..)
                    ret.append(['sstore', lll_to_s_expr(el[1][1]),
                                lll_to_s_expr(ast[i+1])])
                else:
                    ret.append(['mstore', lll_to_s_expr(el[1]),
                                lll_to_s_expr(ast[i+1])])
                i += 2
            elif el == '@':
                ret.append(['mload', ast[i+1]])
                i += 2
            elif el == '@@':
                ret.append(['sload', ast[i+1]])
                i += 2
            else:
                ret.append(lll_to_s_expr(el))
                i += 1
        if i == len(ast)-1:  # (if the last one was +=2 this doesnt happen)
            ret.append(lll_to_s_expr(ast[i]))
        return ret
    elif is_str(ast):
        if len(ast) == 0:
            raise Exception('Zero length strings not allowed in ast')

        if ast[0] == '@':  # @ straight onto a name.
            if ast[1] == '@':
                return ['sload', ast[2:]]
            return ['mload', ast[1:]]

        return ast
    else:
        raise Exception('Dont expect type in AST:', type(ast), ast)


class LLLParser(SExprParser):
    # Class essentially just stops me from having to pass these all the time.
    # Just do SExprParser().parse(), dont neccesarily need a variable.
    def __init__(self, comment_name='scrub'):
        assert comment_name in ['scrub', 'str', 'comment']

        self.start_end = [('[', ']',  True,  False,  'aref'),
                          ('(', ')',  True,  False,  None),
                          ('{', '}',  True,  False,  'seq'),
                          (';', '\n', False, False, comment_name),
                          ('"', '"',  False, False, 'plain', 'str')]
        self.wrong_end_warning = 'warn'
        self.white = [' ', '\t', '\n', ':']
        self.earliest_macro = {}  # Dictionary of functions that act as macros.

    def parse_lll_stream(self, stream, initial=''):
        return lll_to_s_expr(self.parse_stream(stream, initial))

    def parse_lll(self, string):
        return self.parse_lll_stream(io.StringIO(to_str(string)))

    def parse_lll_file(self, file, initial=''):
        with open(file, 'r') as stream:
            tree = self.parse_lll_stream(stream, initial)
        return tree

class LLLWriter:

    def __init__(self, mload='@', mstore='[', sload='@@',sstore='[[', config=None):
        self.config = {} if config is None else config
        def sc(name, to):
            if name not in self.config:
                self.config[name] = to
        sc('mload',  mload)
        sc('mstore', mstore)
        sc('sload',  sload)
        sc('sstore', sstore)
        sc('str',    '"')
        sc('seq',    '{')

    def write_lll_stream(self, stream, tree):
        def w(what):
            stream.write(to_str(what))

        def w_s_tree(val, name, c):
            if name in ['mload','sload']:
                assert len(val) == 2
                if c in ['@','@@']:
                    w(c)
                    return w_tree(val[1])
                elif c == 'var':  # (Note this is not LLL output)
                    if type(val[1]) is str:
                        w(val[1])
                    else:
                        w('(mload ')
                        w_tree(val[1])
                        w(')')
                    return
            elif name in ['mstore', 'sstore']:
                assert len(val) == 3
                if c in ['[', '[[']:
                    w(c)
                    w_tree(val[1])
                    w('] ' if c == '[' else ']] ')
                    return w_tree(val[2])
            elif name == 'seq':
                if c == '{':
                    return w_p_tree(val[1:], '{', '}')
            elif name == 'str':
                assert len(val) == 2
                if c == '"':
                    w(c)
                    w(val[1])
                    return w(c)
            else:
                w_p_tree(val, '(', ')')
            raise Exception('Invalid config', c, val)

        def w_p_tree(val, o, c):
            w(o)
            if len(val) > 0:
                w_tree(val[0])
                for el in val[1:]:
                    w(' ')
                    w_tree(el)
            w(c)

        def w_tree(val):
            if type(val) is list:
                if is_str(val[0]):
                    name = val[0].lower()
                    if name in self.config:
                        c = self.config[name]
                        if c != 'sexpr':
                            return w_s_tree(val, name, c)
                w_p_tree(val, '(', ')')
            else:
                w(val)

        w_tree(tree)

    def write_lll(self, tree):
        stream = io.StringIO()
        self.write_lll_stream(stream, tree)
        stream.seek(0)  # Dont forget to read back!
        return stream.read()
