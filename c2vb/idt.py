from copy import deepcopy

class IDT(object):
    def __init__(self):
        self.identifiers = {}

    def add(self, identifier, type):
        self.identifiers[identifier] = type

    def ask(self, identifier):
        return self.identifiers[identifier]

    def __str__(self):
        return str(self.identifiers)
    
    def copy(self):
        return deepcopy(self)

def type_pri(a, b):
    if a == b:
        return a
    elif 'DOUBLE' in [a, b]:
        return 'DOUBLE'
    elif 'INT' in [a, b]:
        return 'INT'
    else:
        raise Exception('Type can\'t infer %s %s' % (a, b))

def proc(node):
    if (node.type == 'ROOT'):
        node.idt = IDT()
    if node.type in ['DECLARE', 'CONST', 'ARGSDECLARE']:
        for i in node.childs:
            node.idt.add(i.childs[0].value, i.type)
    if node.type in ['DIGIT_CONSTANT', 'STRING_CONSTANT']:
        node.datatype = {float: 'DOUBLE', bool: 'BOOL', int: 'INT', str: 'STRING'}[type(node.value)]
    elif node.type == 'IDENTIFIER':
        node.datatype = node.idt.ask(node.value)
    elif node.type == 'FUNCTIONCALL':
        node.datatype = node.idt.ask(node.childs[0].value)

    for i in node.childs:
        if i.type in ['IF', 'FOR', 'WHILE', 'FUNCDECLARE']:
            if i.type == 'FUNCDECLARE':
                node.idt.add(i.childs[0].value, i.value)
            i.idt = node.idt.copy()
        else:
            i.idt = node.idt
        proc(i)
    if node.value in ['==', '!=', '<', '>', '<=', '>=']:
        node.datatype = 'BOOL'
        node.transtype = type_pri(node.childs[0].datatype, node.childs[1].datatype)
    elif node.value in ['!', '&&', '||']:
        node.datatype = node.transtype = 'BOOL'
    elif node.value in ['~'] or node.type == 'NEG':
        node.datatype = node.transtype = node.childs[0].datatype
    elif node.value in ['+', '-', '*', '/', '%', '~', '&', '|', '^']:
        node.datatype = node.transtype = type_pri(node.childs[0].datatype, node.childs[1].datatype)
        if node.value == '/' and node.datatype == 'INT':
            node.type = 'INTDIV'
