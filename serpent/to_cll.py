from parser import parse_lines
import io
from numerize import is_numberlike

stream = io.open("examples/muck.se", "r") #, encoding="utf-8")

lines = stream.readlines()
print(lines)

print(parse_lines(lines))

def to_cll_document(document):
    return to_cll(parse_lines(document.split('n')))

def to_cll(top, output, t=0, tab='  '):
    def after_tab(what=''):
        for i in range(t):
            output.write(tab)
        output.write(what)
        if tab != '':
            output.write('\n')

    if type(top) is str:
        if is_numberlike(top):
            output.write(' ' + top)
        elif top == 'msg.sender':
            after_tab(' (caller)')
        elif top == 'msg.value':
            after_tab(' (callvalue)')
        elif top == 'msg.datan':
            after_tab(' (calldatasize)')
        else:
            after_tab(' (mload ' + top + ')')

    elif top[0] == 'seq':
        after_tab('{')
        for el in top[1:]:
            to_cll(top, output, t+1, tab=tab)
        after_tab('}')

    else:
        name = top[0]
        rest = top[1:]

        if name == 'access':
            rest = top[2:]
            if top[1] == 'contract.storage':
                name = 'sload'
            elif top[1] == 'msg.data':
                name = 'calldataload'
                after_tab('(calldataload ' + hex(16*int(top[2])) + ')')
                assert len(top) == 2
                return
        elif name == '!':
            name = 'not'
        elif name == 'set':
            name = 'mstore'
        
        after_tab(' (' + name)
        
        for el in rest:
            to_cll(top,output, t+1, tab='')
        output.write(')\n')

#
#list = []
#for line in stream.readlines():
#    list.append(line[:-1])
#
#print(list)
#print(parse_lines(list))

