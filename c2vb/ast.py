from .lexer import operators

TRANS = {
    'INT': 'Long', 'FLOAT': 'Single', 'DOUBLE': 'Double', 'STRING': 'string', 'BOOL': 'Boolean',
    'LOGIC_AND': 'And', 'LOGIC_OR': 'Or', 'LOGIC_Not': 'Not',
    'ARITHMETIC_AND': 'And', 'ARITHMETIC_OR': 'Or', 'ARITHMETIC_NOT': 'Not', 'XOR': 'Xor',
    'PLUS': '+', 'MINUS': '-', 'NEG': '-', 'MUL': '*', 'MOD': 'Mod', 'DIV': '/', 'INTDIV': '\\',
    'GET': '>=', 'LET': '<=', 'LT': '<', 'GT': '>', 'EQUAL': '=', 'NOT_EQUAL': '<>',
}


class ASTnode(object):
    def __init__(self, type, value, childs):
        self.type = type
        self.value = value
        self.childs = []
        for i in childs:
            self.add_child(i)
        self.parent = self

    def add_child(self, node):
        node.parent = self
        self.childs.append(node)

    def __str__(self, r=0):
        ret = '    ' * r + self.type + ' ' + str(self.value) + '\n'
        for i in self.childs:
            ret = ret + i.__str__(r+1)
        return ret

    def dot(self, prefix='n'):
        if prefix == 'n':
            return 'graph\n{\n%s}\n' % self.dot(prefix='n0')
        ret = '    %s;\n' % prefix + \
            '    %s [label=\"%s\"]\n' % (prefix, str(self.value))
        count = 0
        for i in self.childs:
            ret = "%s    %s -- %s\n%s" % (ret, prefix, prefix +
                                          str(count), i.dot(prefix=prefix + str(count)))
            count = count + 1
        return ret

    def vb(self, r=0, shift='    '):
        if self.type == 'IDENTIFIER':
            ret = self.value
            for i in self.childs[0].childs:
                ret = ret + '(%s)' % i.vb()
            return ret
        elif self.type == 'DECLARE':
            ret = ''
            for i in self.childs:
                if len(i.childs) == 1:
                    ret = ret + \
                        '%s As %s, ' % (i.childs[0].vb(), TRANS[i.type])
                else:
                    ret = ret + \
                        '%s As %s = %s, ' % (
                            i.childs[0].vb(), TRANS[i.type], i.childs[1].vb())
            return shift*r + 'Dim ' + ret[0:-2] + '\n'
        elif self.type == 'ARGSDECLARE':
            ret = ''
            for arg in self.childs:
                identifier = arg.childs[0].vb()
                ret = ret + '%s As %s, ' % (identifier, TRANS[arg.type])
            return ret[:-2]
        elif self.type == 'FUNCDECLARE':
            identifier = self.childs[0].vb()
            parameters = self.childs[1].vb()
            statements = self.childs[2].vb(r=r+1)
            if self.value == 'VOID':
                return 'Sub %s(%s)\n%sEnd Sub\n' % (identifier, parameters, statements)
            else:
                return 'Function %s(%s) As %s\n%sEnd Function\n' % (identifier, parameters, TRANS[self.value], statements)
        elif self.type == 'STATEMENT':
            return shift*r + self.childs[0].vb() + '\n'
        elif self.type == 'STATEMENTS':
            ret = ''
            for i in self.childs:
                ret = ret + i.vb(r=r)
            return ret
        elif self.type == 'ASSIGN':
            return self.childs[0].vb() + ' = ' + self.childs[1].vb()
        elif self.type == 'ASSIGNS':
            ret = ''
            for assign in self.childs:
                ret = ret + assign.vb() + ': '
            return ret[:-2]
        elif self.type == 'IF':
            ret = shift*r + \
                'If %s Then\n' % self.childs[0].vb() + self.childs[1].vb(r=r+1)
            if (len(self.childs) == 3):
                ret = ret + shift*r + 'Else\n' + \
                    self.childs[2].vb(r=r+1)
            ret = ret + shift*r + 'End If\n'
            return ret
        elif self.type == 'WHILE':
            print(self)
            return shift*r + 'Do While ' + self.childs[0].vb() + '\n' + \
                self.childs[1].vb(r=r+1) + \
                shift*r + 'Loop\n'
        elif self.type == 'FOR':
            self.type, self.value = 'WHILE', 'while'
            return shift*r + self.childs[0].vb() + ['', '\n'][self.childs[0].type == 'ASSIGNS'] + \
                shift*r + 'Do While ' + self.childs[1].vb() + '\n' + \
                self.childs[3].vb(r=r+1) + \
                shift*(r+1) + self.childs[2].vb() + '\n' + \
                shift*r + 'Loop\n'
        elif self.type == 'FUNCTIONCALL':
            identifier = self.childs[0].vb()
            if self.idt.ask(identifier) == 'VOID':
                ret = shift*r + identifier + ' ' + \
                    self.childs[1].vb() + '\n'
                return ret
            else:
                ret = identifier + '(' + self.childs[1].vb() + ')'
                return ret
        elif self.type == 'ARGS':
            ret = ''
            for i in self.childs:
                ret = ret + i.vb() + ', '
            return ret[0:-2]
        elif self.type == 'CONST':
            ret = ''
            for i in self.childs:
                ret = ret + \
                    '%s As %s = %s, ' % (
                        i.childs[0].vb(), TRANS[i.type], i.childs[1].vb())
            return 'Const ' + ret[0:-2] + '\n'
        elif self.type == 'DIGIT_CONSTANT':
            return str(self.value)
        elif self.type == 'STRING_CONSTANT':
            return '\"%s\"' % self.value
        elif self.type == 'ROOT':
            ret = ''
            for i in self.childs:
                ret = ret + i.vb()
            return ret
        elif self.type == 'BREAK':
            loop = ''
            f = self.parent
            while True:
                if f.type == 'FOR':
                    return shift*r + 'Exit For\n'
                elif f.type == 'WHILE':
                    return shift*r + 'Exit Do\n'
                assert(self.type != 'ROOT')
                f = f.parent
        elif self.type == 'RETURN':
            p = self.parent
            while True:
                if p.type == 'FUNCDECLARE':
                    if p.value == 'VOID':
                        return shift*r + 'Exit Sub\n'
                    else:
                        identifier = p.childs[0].vb()
                        expr = self.childs[0].vb()
                        return shift*r + identifier + ' = ' + expr + '\n' + \
                            shift*r + 'Exit Function\n'
                p = p.parent
        elif self.value in operators:
            if self.type in ['LOGIC_NOT', 'NEG', 'ARITHMETIC_NOT']:
                return TRANS[self.type]+self.childs[0].vb()
            else:
                return '('+self.childs[0].vb()+' '+TRANS[self.type]+' '+self.childs[1].vb()+')'
