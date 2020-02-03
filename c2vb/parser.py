from .lexer import keywords
from .ast import ASTnode
DATATYPE = keywords[0]


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.length = len(self.tokens)
        self.analyze()

    def forward(self, s, index):
        if self.tokens[index].type != s and self.tokens[index].value != s:
            raise Exception('不符合预期，预期 %s 实际 %s' %
                            (str(s), str(self.tokens[index].type)))
        index = index + 1
        return index

    def match(self, s, index):
        if type(s) == str:
            s = [s]
        assert(type(s) == list)
        return index < self.length and (self.tokens[index].type in s or self.tokens[index].value in s)

    def _logic_or(self, index):
        node, index = self._logic_and(index)
        while self.match(['||'], index):
            op = self.tokens[index]
            r, index = self._logic_and(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _logic_and(self, index):
        node, index = self._arc_or(index)
        while self.match(['&&'], index):
            op = self.tokens[index]
            r, index = self._arc_or(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _arc_or(self, index):
        node, index = self._arc_xor(index)
        while self.match(['|'], index):
            op = self.tokens[index]
            r, index = self._arc_xor(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _arc_xor(self, index):
        node, index = self._arc_and(index)
        while self.match(['^'], index):
            op = self.tokens[index]
            r, index = self._arc_and(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _arc_and(self, index):
        node, index = self._equal(index)
        while self.match(['&'], index):
            op = self.tokens[index]
            r, index = self._equal(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _equal(self, index):
        node, index = self._compare(index)
        while self.match(['==', '!='], index):
            op = self.tokens[index]
            r, index = self._compare(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _compare(self, index):
        node, index = self._shift(index)
        while self.match(['<', '<=', '>', '>='], index):
            op = self.tokens[index]
            r, index = self._shift(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _shift(self, index):
        node, index = self._add(index)
        while self.match(['<<', '>>'], index):
            op = self.tokens[index]
            r, index = self._add(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _add(self, index):
        node, index = self._mul(index)
        while self.match(['+', '-'], index):
            op = self.tokens[index]
            r, index = self._mul(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _mul(self, index):
        node, index = self._unary(index)
        while self.match(['*', '/', '%'], index):
            op = self.tokens[index]
            r, index = self._unary(index+1)
            node = ASTnode(op.type, op.value, [node, r])
        return node, index

    def _unary(self, index):
        if self.match(['!', '-', '~'], index):
            opt = self.tokens[index]
            index = index + 1
            node, index = self._unary(index)
            if opt.type == 'MINUS':
                opt.type = 'NEG'
            return ASTnode(opt.type, opt.value, [node]), index
        else:
            return self._primary(index)

    def _primary(self, index):
        if self.tokens[index].type == 'DIGIT_CONSTANT':
            return self._digit(index)
        elif self.tokens[index].type == 'LL_BRACKET':
            index = index + 1
            node, index = self._expr(index)
            index = self.forward('RL_BRACKET', index)
            return node, index
        elif self.tokens[index].type == 'IDENTIFIER':
            identifier, next_index = self._identifier(index)
            if self.tokens[next_index].type == 'LL_BRACKET':
                return self._func_call(index)
            else:
                return identifier, next_index
        elif self.tokens[index].type == 'STRING_CONSTANT':
            return ASTnode('STRING_CONSTANT', self.tokens[index].value, []), index + 1

    def _func_call(self, index):
        identifier, index = self._identifier(index)
        index = self.forward('(', index)
        args, index = self._args(index)
        index = self.forward(')', index)
        return ASTnode('FUNCTIONCALL', 'func_call', [identifier, args]), index

    def _digit(self, index):
        return ASTnode('DIGIT_CONSTANT', self.tokens[index].value, []), index + 1

    def _expr(self, index):
        return self._logic_or(index)

    def _args(self, index):
        node = ASTnode('ARGS', 'args', [])
        while True:
            t, index = self._expr(index)
            node.add_child(t)
            if self.tokens[index].type == 'COMMA':
                index = self.forward('COMMA', index)
            else:
                break
        return node, index

    def _identifier(self, index):
        identifier = self.tokens[index].value
        index = index + 1
        assert(index < self.length)
        siz = []
        while self.tokens[index].type == 'LM_BRACKET':
            index = index + 1
            t, index = self._expr(index)
            siz.append(t)
            index = self.forward('RM_BRACKET', index)
        assert(index < self.length)
        return ASTnode('IDENTIFIER', identifier, [ASTnode('ARRAY', 'array', siz)]), index

    def _assign(self, index):
        node = ASTnode('ASSIGN', 'assign', [])
        if self.match('IDENTIFIER', index):
            identifier, index = self._identifier(index)
            node.add_child(identifier)
            if self.match('=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(expr)
                return node, index
            elif self.match('+=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('PLUS', '+', [identifier, expr]))
                return node, index
            elif self.match('-=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('MINUS', '-', [identifier, expr]))
                return node, index
            elif self.match('*=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('MUL', '*', [identifier, expr]))
                return node, index
            elif self.match('/=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('DIV', '/', [identifier, expr]))
                return node, index
            elif self.match('%=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('MOD', '%', [identifier, expr]))
                return node, index
            elif self.match('&=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(
                    ASTnode('ARITHMETIC_AND', '&', [identifier, expr]))
                return node, index
            elif self.match('|=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(
                    ASTnode('ARITHMETIC_OR', '|', [identifier, expr]))
                return node, index
            elif self.match('^=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(ASTnode('XOR', '^', [identifier, expr]))
                return node, index
            elif self.match('++', index):
                index = index + 1
                node.add_child(
                    ASTnode('PLUS', '+', [node.childs[0],
                                          ASTnode('DIGIT_CONSTANT', 1, [])])
                )
                return node, index
            elif self.match('--', index):
                index = index + 1
                node.add_child(
                    ASTnode('MINUS', '-', [node.childs[0],
                                           ASTnode('DIGIT_CONSTANT', 1, [])])
                )
                return node, index
            else:
                raise Exception('不可识别的符号 %s, index: %d' %
                                (str(self.tokens[index]), index))
        elif self.match('++', index):
            index = index + 1
            identifier, index = self._identifier(index)
            node.add_child(identifier)
            node.add_child(
                ASTnode('PLUS', '+', [node.childs[0],
                                      ASTnode('DIGIT_CONSTANT', 1, [])])
            )
            return node, index
        elif self.match('--', index):
            index = index + 1
            identifier, index = self._identifier(index)
            node.add_child(identifier)
            node.add_child(
                ASTnode('MINUS', '-', [node.childs[0],
                                       ASTnode('DIGIT_CONSTANT', 1, [])])
            )
            return node, index
        else:
            raise Exception('不可识别的符号 %s, index: %d' %
                            (str(self.tokens[index]), index))

    def _assigns(self, index):
        node = ASTnode('ASSIGNS', 'assigns', [])
        while self.match(['IDENTIFIER', '++', '--'], index):
            assign, index = self._assign(index)
            node.add_child(assign)
            if not self.match(',', index):
                break
            index = self.forward('COMMA', index)
        return node, index

    def _declare(self, index):
        node = ASTnode('DECLARE', 'declare', [])
        data_t = self.tokens[index]
        index = index + 1

        while self.tokens[index].type == 'IDENTIFIER':
            identifier, index = self._identifier(index)
            assert(index < self.length)
            if self.match('=', index):
                index = index + 1
                expr, index = self._expr(index)
                node.add_child(
                    ASTnode(data_t.type, data_t.value, [identifier, expr]))
            else:
                node.add_child(
                    ASTnode(data_t.type, data_t.value, [identifier]))
            if self.match(',', index):
                index = index + 1

        index = self.forward('SEMICOLON', index)
        return node, index

    def _const(self, index):
        index = self.forward('CONST', index)
        node, index = self._declare(index)
        node.type, node.value = 'CONST', 'const'
        for i in node.childs:
            assert(len(i.childs) == 2)
        return node, index

    def _statements(self, index):
        ret = ASTnode('STATEMENTS', 'statements', [])
        while self.match(['IDENTIFIER', 'IF', 'CONST', 'FOR', '{', 'RETURN', 'BREAK', 'WHILE'] + DATATYPE, index):
            node, index = self._statement(index, p='statements')
            ret.add_child(node)
        return ret, index

    def _statement(self, index, p=''):
        if self.match('IF', index):
            return self._if(index)
        elif self.match(DATATYPE, index):
            return self._declare(index)
        elif self.match('CONST', index):
            return self._const(index)
        elif self.match('WHILE', index):
            return self._while(index)
        elif self.match('FOR', index):
            return self._for(index)
        elif self.match('{', index):
            index = self.forward('{', index)
            node, index = self._statements(index)
            index = self.forward('}', index)
            return node, index
        elif self.match('RETURN', index):
            if p == 'statements':
                return self._return(index)
            else:
                ret, index = self._return(index)
                return ASTnode('STATEMENTS', 'statements', [ret]), index
        elif self.match('BREAK', index):
            index = index + 1
            index = self.forward(';', index)
            return ASTnode('BREAK', 'break', []), index
        elif self.match('(', index+1):
            node, index = self._func_call(index)
            index = self.forward(';', index)
            return node, index
        else:
            node = ASTnode('STATEMENT', 'statement', [])
            assigns, index = self._assigns(index)
            node.add_child(assigns)
            index = self.forward(';', index)
            return node, index

    def _return(self, index):
        index = self.forward('RETURN', index)
        if self.match(';', index):
            index = index + 1
            return ASTnode('RETURN', 'return', []), index
        expr, index = self._expr(index)
        index = self.forward(';', index)
        return ASTnode('RETURN', 'return', [expr]), index

    def _while(self, index):
        index = self.forward('WHILE', index)
        index = self.forward('(', index)
        condition, index = self._expr(index)
        index = self.forward(')', index)
        statement, index = self._statement(index)
        return ASTnode('WHILE', 'while', [condition, statement]), index

    def _for(self, index):
        index = self.forward('FOR', index)
        index = self.forward('LL_BRACKET', index)
        node = ASTnode('FOR', 'for', [])
        if self.match(DATATYPE, index):
            st, index = self._declare(index)
            node.add_child(st)
        else:
            st, index = self._assigns(index)
            index = self.forward(';', index)
            node.add_child(st)
        condition, index = self._expr(index)
        node.add_child(condition)
        index = self.forward('SEMICOLON', index)
        step, index = self._assigns(index)
        node.add_child(step)
        index = self.forward('RL_BRACKET', index)
        statement, index = self._statement(index)
        node.add_child(statement)
        return node, index

    def _if(self, index):
        index = self.forward('IF', index)
        node = ASTnode('IF', 'if', [])
        index = self.forward('LL_BRACKET', index)
        condition, index = self._expr(index)
        node.add_child(condition)
        index = self.forward('RL_BRACKET', index)
        yes, index = self._statement(index)
        node.add_child(yes)
        if self.match('ELSE', index):
            index = self.forward('ELSE', index)
            no, index = self._statement(index)
            node.add_child(no)
        return node, index

    def _func_declare(self, index):
        if not self.match(DATATYPE, index):
            raise Exception("不可识别的数据类型")
        node = ASTnode('FUNCDECLARE', self.tokens[index].type, [])
        index = index + 1
        identifier, index = self._identifier(index)
        node.add_child(identifier)
        index = self.forward('(', index)
        args = ASTnode('ARGSDECLARE', 'args_declare', [])
        while self.match(DATATYPE, index):
            dec = ASTnode(self.tokens[index].type,
                          self.tokens[index].value, [])
            index = index + 1
            arg, index = self._identifier(index)
            dec.add_child(arg)
            args.add_child(dec)
            if not self.match(',', index):
                break
            index = index + 1
        node.add_child(args)
        index = self.forward(')', index)
        statement, index = self._statement(index)
        node.add_child(statement)
        return node, index

    def analyze(self):
        index = 0
        root = ASTnode('ROOT', 'root', [])
        while index < self.length:
            if self.match('CONST', index):
                dec, index = self._const(index)
                root.add_child(dec)
            elif self.match('(', index + 2):
                func, index = self._func_declare(index)
                root.add_child(func)
            else:
                dec, index = self._declare(index)
                root.add_child(dec)
        self.ast = root
        return self.ast
