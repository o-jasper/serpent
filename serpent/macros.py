
gensym_i = 0

def gensym(name='__G'):  # Symbol 'guaranteed' to be unique.
    gensym_i += 1
    return name + str(gensym_i)


def _access(ast):
    if ast[1] == 'msg.data':
        return ['calldataload', ast[2]]
    elif ast[1] == 'contract.storage':
        return ['sload', ast[2]]


def _array_lit(ast):
    o = ['array', str(len(ast[1:]))]
    for a in ast[1:]:
        o = ['set_and_inc', a, o]
    return ['-', o, str(len(ast[1:])*32)]


def _import(ast): # Import is to be used specifically for creates
    return ['code', parse(open(ast[1]).read())]


def _inset(ast): # Inset is to be used like a macro in C++
    return parse(open(ast[1]).read())

def _return(ast):
    if len(ast) == 2 and ast[1][0] == 'array_lit':
        return ['return', ast[1], str(len(ast[1][1:]))]

    
def _if(ast):
    return ['ifelse' if len(ast) == 4 else 'if'] + ast[1:]


def _set(ast):
    if ast[1][0] == 'access':
        if ast[1][1] == 'contract.storage':
            return ['sstore', ast[1][2], ast[2]]
        else:
            return ['arrset', ast[1][1], ast[1][2], ast[2]]


def _funcall(ast):  # Call contract as function.
    return ['msg', ast[1], '0', ['-', 'tx.gas', msg_gas],
            ['array_lit'] + ast[2:], str(len(ast)-2)]

## Case. (idea to have parser uuse this.)
def subcase(var, ast):
    if len(ast) == 0:  #Got nothing.
        return ["seq"]

    assert type(ast[0]) is list and len(ast[0]) == 2

    if ast[0][0] == 'otherwise':
        assert len(ast) == 1  # Must be last case.
        return ast[0][1]
    else:
        return ["ifelse", ["=", var, ast[0][0]],
                ast[0][1], subcase(var, ast[1:])]

def _case(ast):
    var = gensym()
    return ['seq',
            ['set', var, ast[1]],   # Put into parameter.
            subcase(var, ast[2:])]  # Generate a lot of `ifelse`s with the param.

## Cond.
def raw_cond(ast):
    if len(ast) == 0:
        return ["seq"]

    assert type(ast[0]) is list and len(ast[0]) == 2

    if ast[0][0] == "otherwise":
        assert len(ast) == 1  # Always runs, must be last.
        return ast[0][1]
    else:
        return ["ifelse", ast[0][0], ast[0][1], raw_cond(ast[1:])]


def _cond(ast):
    return raw_cond(ast[1:])


dont_recurse = ['access', 'if']
# Note: lambda not easy enough to use, apparently.
macros = {
    'access' : _access,
    'array_lit' : _array_lit,
    'import'   : _import,
    'inset'    : _inset,
    'return' : _return,
    'if'     : _if,
    'set'    : _set,
    'access' : _access,

    'funcall' : _funcall,
    'case'    : _case,
# This one is for the lispers.(for them the ifelse construct is too nested)
    'cond'    : _cond
}

#def _code(ast): # Doesnt really do anything? Just check number of args instead?
#    return ['code', ast[1]]

def macroexpand_list(list):
    ret = []
    for el in list:
        ret.append(macroexpand(el))
    return ret


# Note: might be better to use compiler.py's `funtable`
# also some more internal stuff either needs exemption of to be pulled in
# as macros.
fun_exempt = ['+', '-', '*', '/', '^', '%', '#/', '#%', '==', '<',
            '<=','>','>=','!','or','||','and','&&','xor','&','|',
            'byte','pop','array','setch','string','sha3','sha3bytes',
            'sload','sstore','calldataload','id','return','return',
            'suicide','if','ifelse','while','init','code',
            'set_and_inc','msg']

def is_exempt(name): 
    return name in fun_exempt
    

msg_gas = '21'  # Drinking age.

def if_not_macro(ast):  # Thing to do if it isnt a macro.
    if is_exempt(ast[0]):
        return None
    elif type(ast[0]) is str:
         # Equivalent to calling the 'funcall' macro.
        return _funcall(['funcall'] + ast)  # (['funcall'] + ast)
    # If you want to use a returned value as the address, use `funcall` directly.
    else:
        raise Exception("No behavior defined for this", ast)


def macroexpand_1(ast):
    if ast[0] in macros:
        return macros[ast[0]](ast)
    else:
        return if_not_macro(ast)

def macroexpand(ast):
    if type(ast) is list:
        ret = macroexpand_1(ast)

        if ast[0] in dont_recurse:
            return ast if (ret is None) else ret
        elif ret is None:
            return macroexpand_list(ast)
        else:
            return macroexpand(ret)
    else:
        return ast
