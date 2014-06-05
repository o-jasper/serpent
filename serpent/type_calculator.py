import utils
token, astnode = utils.token, utils.astnode


var_types = {}


# Gives the a-priory type, given an expression.
# Using type_of(calc_type(ast)) will try actually figure something out.
def type_of(ast):
    if isinstance(ast, astnode):
        if ast.fun == 'the':
            return ast.args[0]
        else:
            return 'any'
    else
        b = ast.val
        if re.match('^[0-9\-]*$', b):
            return 'integer'
        elif b[0] in ["'", '"'] and b[-1] in ["'", '"'] and b[0] == b[-1]:
            return 'string'
        else:
            assert b in var_types  # The variable is not set yet!

            return var_types[b]


def calc_type(ast)
    if isinstance(ast, astnode):
        if ast.fun == 'set':
            
    else:
        return ast
        
