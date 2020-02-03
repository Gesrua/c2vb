from .lexer import Lexer
from .parser import Parser
from .idt import proc

def run(file=None, src=None):
    if file == None and src == None:
        raise Exception('No file or src given')
    if file != None and src != None:
        raise Exception('Can\'t give src and file at same time')
    f = open(file, 'r')
    lines = f.readlines()
    src = ''
    for i in lines:
        if i[0] == '#':
            if i.find('include') == 1:
                raise Exception('不支持 include')
            else:
                print('宏将被忽略')
        else:
            src = src + i
    lex = Lexer(src)
    parser = Parser(lex.tokens)
    proc(parser.ast)
    return parser.ast.vb()


