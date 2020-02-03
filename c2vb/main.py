from .lexer import Lexer
from .parser import Parser
from .idt import proc

def run(file=None, src=None):
    if file == None and src == None:
        raise Exception('No file or src given')
    if file != None and src != None:
        raise Exception('Can\'t give src and file at same time')
    f = open(file, 'r')
    src = f.read()
    lex = Lexer(src)
    parser = Parser(lex.tokens)
    proc(parser.ast)
    return parser.ast.vb()


