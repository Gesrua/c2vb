TOKEN_STYLE = [
    'KEY_WORD', 'IDENTIFIER', 'DIGIT_CONSTANT',
    'OPERATOR', 'SEPARATOR', 'STRING_CONSTANT'
]

DETAIL_TOKEN_STYLE = {
    'include': 'INCLUDE',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'string': 'STRING',
    'double': 'DOUBLE',
    'void': 'VOID',
    'bool': 'BOOL',
    'for': 'FOR',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'return': 'RETURN',
    'break': 'BREAK',
    '=': 'ASSIGN',
    '<': 'LT',
    '>': 'GT',
    '++': 'SELF_PLUS_ONE',
    '--': 'SELF_MINUS_ONE',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '%': 'MOD',
    '>=': 'GET',
    '<=': 'LET',
    '(': 'LL_BRACKET',
    ')': 'RL_BRACKET',
    '{': 'LB_BRACKET',
    '}': 'RB_BRACKET',
    '[': 'LM_BRACKET',
    ']': 'RM_BRACKET',
    ',': 'COMMA',
    '"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON',
    '#': 'SHARP',
    '==': 'EQUAL',
    '!=': 'NOT_EQUAL',
    '&&': 'LOGIC_AND',
    '||': 'LOGIC_OR',
    '!': 'LOGIC_NOT',
    '~': 'ARITHMETIC_NOT',
    '&': 'ARITHMETIC_AND',
    '|': 'ARITHMETIC_OR',
    '<<': 'SHIFT_LEFT',
    '>>': 'SHIFT_RIGHT',
    '^': 'XOR',
    '+=': 'SELF_PLUS',
    '-=': 'SELF_MINUS',
    '*=': 'SELF_MUL',
    '/=': 'SELF_DIV',
    '%=': 'SELF_MOD',
    '|=': 'SELF_OR',
    '&=': 'SELF_AND',
    '^=': 'SELF_XOR',
    'const': 'CONST'
}

keywords = [
    ['int', 'float', 'double', 'char', 'void', 'string', 'bool'],
    ['if', 'for', 'while', 'do', 'else'],
    ['include', 'return', 'break'],
    ['const']
]

operators = [
    '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
    '++', '--',
    '+', '-', '*', '/', '%', '~', '&', '|', '^', '<<', '>>',
    '!', '&&', '||',
    '==', '!=', '<', '>', '<=', '>='
]

delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

blanks = [' ', '\n', '\r', '\t']


def is_blank(c):
    return c in blanks


def is_delimiters(c):
    return c in delimiters


def is_operators(c):
    return c in operators


class Token(object):
    def __init__(self, type_index, value):
        if (type_index == 0 or type_index == 3 or type_index == 4):
            self.type = DETAIL_TOKEN_STYLE[value]
        else:
            self.type = TOKEN_STYLE[type_index]
        self.value = value

    def __str__(self):
        return self.type + ' ' + str(self.value)


class Lexer(object):
    def __init__(self, s):
        self.tokens = []
        self.content = s
        self.length = len(s)
        self.analyze()

    def is_blank(self, index):
        return is_blank(self.content[index])

    def is_delimiters(self, index):
        return is_delimiters(self.content[index])

    def is_operators(self, index):
        return is_operators(self.content[index])

    def skip_blank(self, index):
        while index < self.length and self.is_blank(index):
            index = index + 1
        return index

    def get_token(self, index):
        s = ''
        c = self.content[index]

        if index + 1 < self.length and self.content[index] == '/' and self.content[index+1] == '/':
            while index < self.length and self.content[index] != '\n':
                index = index + 1
            return (index, None)

        # string
        if c == '\"' or c == '\'':
            s = c
            index = index + 1
            while index < self.length:
                s = s + self.content[index]
                if self.content[index] == c and self.content[index-1] != '\\':
                    index = index + 1
                    break
                index = index + 1
            return (index, Token(5, eval(s)))

        # digit
        if c.isdigit():
            while index < self.length and not self.is_blank(index) and not self.is_delimiters(index) and not self.is_operators(index):
                s = s + self.content[index]
                index = index + 1
            return (index, Token(2, eval(s)))

        if (is_delimiters(c)):
            return (index+1, Token(4, c))

        if index+1 < self.length:
            cc = c + self.content[index+1]
            if (is_operators(cc)):
                return (index+2, Token(3, cc))
        if (is_operators(c)):
            return (index+1, Token(3, c))

        while index < self.length and not self.is_delimiters(index) and not self.is_blank(index) and not self.is_operators(index):
            s = s + self.content[index]
            index = index + 1

        for i in range(0, 4):
            if s in keywords[i]:
                return (index, Token(0, s))

        if s == 'true':
            return index, Token(2, True)
        elif s == 'false':
            return index, Token(2, False)

        return (index, Token(1, s))

    def analyze(self):
        i = 0
        i = self.skip_blank(i)
        while i < self.length:
            i, tok = self.get_token(i)
            if (tok != None):
                self.tokens.append(tok)
            i = self.skip_blank(i)
