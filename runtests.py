#!/usr/bin/python
import sys
from serpent import parser, rewriter, compiler, write_serpent, utils
t = open('tests.txt').readlines()
i = 0

print(write_serpent.serialize_expr(utils.nodeify('+', ['a', 'b'])))

while 1:
    o = []
    while i < len(t) and (not len(t[i]) or t[i][0] != '='):
        o.append(t[i])
        i += 1
    i += 1
    print '================='
    text = '\n'.join(o).replace('\n\n', '\n')
    ast = parser.parse(text)
    print(':' + text + ':')

    text2 = str(write_serpent.serialize(ast))
    print(':' + text2 + ':')
    ast_cpy = parser.parse(text2)
    if utils.denodeify(ast) != utils.denodeify(ast_cpy):
        print( "BUG: does not match!", ast, ast_cpy)

    print "AST:", ast
    print ""
    ast2 = rewriter.compile_to_lll(ast)
    print "LLL:", ast2
    print ""
    varz = rewriter.analyze(ast)
    print "Analysis: ", varz
    print ""
    aevm = compiler.compile_lll(ast2)
    print "AEVM:", ' '.join([str(x) for x in aevm])
    print ""
    code = compiler.assemble(aevm)
    print "Output:", code.encode('hex')
    if i >= len(t):
        break
