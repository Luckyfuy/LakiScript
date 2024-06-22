#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from lk_error import InvalidSyntaxError
from lk_ast_node import *

# 语法解析结果
class ParserResult(object):

    def __init__(self):
        self.error = None
        self.node = None
        self.advance_cnt = 0
        self.to_reverse_cnt = 0

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

    def registerAdvancement(self):
        self.advance_cnt += 1

    def register(self, res):
        self.advance_cnt += res.advance_cnt
        if res.error is not None:
            self.error = res.error
        return res.node

    def tryRegister(self, res):
        if res.error:
            self.to_reverse_cnt = res.advance_cnt
            return None
        return self.register(res)

# 语法解析器
class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def reverse(self, amount=1):
        '''
        回退，反向advance
        '''
        self.token_index -= amount
        self.updateCurrentToken()
        return self.current_token

    def updateCurrentToken(self):
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def parse(self):
        res = self.statements()
        if res.error is None and self.current_token.type != T_EOF:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' or '/'"))
        return res

    def statements(self):
        '''
        statements -> NEWLINE* expr (NEWLINE+ statement)* NEWLINE*
        '''
        res = ParserResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == T_NEWLINE:
            res.registerAdvancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error is not None:
            return res
        statements.append(statement)

        more_statements = True
        while True:
            newline_cnt = 0
            while self.current_token.type == T_NEWLINE:
                res.registerAdvancement()
                self.advance()
                newline_cnt += 1
            if newline_cnt == 0:
                more_statements = False
            if not more_statements:
                break
            statement = res.tryRegister(self.statement())
            if statement is None:
                self.reverse(res.to_reverse_cnt)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_token.pos_end.copy()))

    def statement(self):
        '''
        statement -> KEYWORD:return expr?
                  -> KEYWORD:continue
                  -> KEYWORD:break
                  -> expr
        '''
        res = ParserResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.match(T_KEYWORD, 'return'):
            res.registerAdvancement()
            self.advance()

            expr = res.tryRegister(self.expr())
            if expr is None:
                self.reverse(res.to_reverse_cnt)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        elif self.current_token.match(T_KEYWORD, 'continue'):
            res.registerAdvancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))

        elif self.current_token.match(T_KEYWORD, 'break'):
            res.registerAdvancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error is not None:
            return res
        return res.success(expr)

    def expr(self):
        '''
        expr -> KEYWORD: var IDENTIFIER EQ expr
             -> IDENTIFIER EQ expr
             -> comp (( KEYWORD: and | KEYWORD: or ) comp)*
        '''
        res = ParserResult()

        if self.current_token.match(T_KEYWORD, 'var'):
            res.registerAdvancement()
            self.advance()

            if self.current_token.type != T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, 'Expected identifier'))
            var_name = self.current_token
            res.registerAdvancement()
            self.advance()

            if self.current_token.type != T_EQ:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '='"))
            res.registerAdvancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error is not None:
                return res
            return res.success(VarAssignNode(var_name, expr, T_EQ))

        if self.current_token.type == T_IDENTIFIER:
            var_name = self.current_token
            res.registerAdvancement()
            self.advance()

            if self.current_token.type not in EQS:
                self.reverse()
                node = res.register(self.binOp(self.comp, ((T_KEYWORD, 'and'), (T_KEYWORD, 'or'))))
                if res.error is not None:
                    return res
                return res.success(node)
            eq = self.current_token.type
            res.registerAdvancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error is not None:
                return res
            return res.success(VarAssignNode(var_name, expr, eq, False))

        else:
            node = res.register(self.binOp(self.comp, ((T_KEYWORD, 'and'), (T_KEYWORD, 'or'))))
            if res.error is not None:
                return res
            return res.success(node)

    def comp(self):
        '''
        comp -> KEYWORD: not comp
             -> arith (( EE | NE | LT | GT | LTE | GTE ) arith)*
        '''
        res = ParserResult()

        if self.current_token.match(T_KEYWORD, 'not'):
            token = self.current_token
            res.registerAdvancement()
            self.advance()
            node = res.register(self.comp())
            if res.error is not None:
                return res
            return res.success(UnaryOpNode(token, node))

        else:
            node = res.register(self.binOp(self.arith, (T_EE, T_NE, T_LT, T_GT, T_LTE, T_GTE)))
            if res.error is not None:
                return res
            return res.success(node)

    def arith(self):
        '''
        arith -> term (( PLUS | MINUS ) term)*
        '''
        return self.binOp(self.term, (T_PLUS, T_MINUS))

    def term(self):
        '''
        term -> factor (( MUL | DIV | MOD ) factor)*
        '''
        return self.binOp(self.factor, (T_MUL, T_DIV, T_MOD))

    def factor(self):
        '''
        factor -> ( PLUS | MINUS ) factor
               -> power
        '''
        res = ParserResult()
        token = self.current_token

        if token.type in (T_PLUS, T_MINUS):
            res.registerAdvancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error is not None:
                return res
            return res.success(UnaryOpNode(token, factor))
        return self.power()

    def power(self):
        '''
        power -> call (POW factor)*
        '''
        return self.binOp(self.call, (T_POW, ), self.factor)

    def call(self):
        '''
        call -> atom ( LPAREN ( IDENTIFIER (COMMA IDENTIFIER)* )? RPAREN )?
        '''
        res = ParserResult()

        atom = res.register(self.atom())
        if res.error is not None:
            return res

        if self.current_token.type == T_LPAREN:
            res.registerAdvancement()
            self.advance()
            arg_node = []

            if self.current_token.type == T_RPAREN:
                res.registerAdvancement()
                self.advance()
            else:
                arg_node.append(res.register(self.expr()))
                if res.error is not None:
                    return res

                while self.current_token.type == T_COMMA:
                    res.registerAdvancement()
                    self.advance()
                    arg_node.append(res.register(self.expr()))
                    if res.error is not None:
                        return res

                if self.current_token.type != T_RPAREN:
                    return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ',' or ')'"))
                res.registerAdvancement()
                self.advance()

            return res.success(CallNode(atom, arg_node))
        return res.success(atom)

    def atom(self):
        '''
        atom -> INT | FLOAT | STRING | IDENTIFIER
             -> LPAREN expr RPAREN
             -> list-expr
             -> if-expr
             -> for-expr
             -> while-expr
             -> func-expr
        '''
        res = ParserResult()
        token = self.current_token

        if token.type in (T_INT, T_FLOAT):
            res.registerAdvancement()
            self.advance()
            return res.success(NumberNode(token))

        elif token.type == T_STRING:
            res.registerAdvancement()
            self.advance()
            return res.success(StringNode(token))

        elif token.type == T_IDENTIFIER:
            res.registerAdvancement()
            self.advance()
            return res.success(VarAccessNode(token))

        elif token.type == T_LBRACKET:
            list_expr = res.register(self.listExpr())
            if res.error is not None:
                return res
            return res.success(list_expr)

        elif token.type == T_LPAREN:
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error is not None:
                return res

            if self.current_token.type == T_RPAREN:
                res.registerAdvancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ')'"))

        elif token.match(T_KEYWORD, 'if'):
            if_expr = res.register(self.ifExpr())
            if res.error is not None:
                return res
            return res.success(if_expr)

        elif token.match(T_KEYWORD, 'for'):
            for_expr = res.register(self.forExpr())
            if res.error is not None:
                return res
            return res.success(for_expr)

        elif token.match(T_KEYWORD, 'while'):
            while_expr = res.register(self.whileExpr())
            if res.error is not None:
                return res
            return res.success(while_expr)

        elif token.match(T_KEYWORD, 'func'):
            func_expr = res.register(self.funcExpr())
            if res.error is not None:
                return res
            return res.success(func_expr)

        return res.failure(InvalidSyntaxError(token.pos_start, token.pos_end, "Expected int, float, identifier or '('"))

    def listExpr(self):
        '''
        list-expr -> LBRACKET ( expr (COMMA expr)* )? RBRACKET
        '''
        res = ParserResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != T_LBRACKET:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '['"))
        res.registerAdvancement()
        self.advance()

        if self.current_token.type == T_RBRACKET:
            res.registerAdvancement()
            self.advance()
        else:
            elements.append(res.register(self.expr()))
            if res.error is not None:
                return res

            while self.current_token.type == T_COMMA:
                res.registerAdvancement()
                self.advance()
                elements.append(res.register(self.expr()))
                if res.error is not None:
                    return res

            if self.current_token.type != T_RBRACKET:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ',' or ']'"))
            res.registerAdvancement()
            self.advance()

        return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))

    def ifExpr(self):
        '''
        if-expr -> KEYWORD:if expr LBRACE statements RBRACE
                   ( KEYWORD:elif expr LBRACE statements RBRACE )*
                   ( KEYWORD:else LBRACE statements RBRACE )?
        '''
        res = ParserResult()
        case = [] # if + 多个elif
        else_case = None

        if not self.current_token.match(T_KEYWORD, 'if'):
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'if'"))
        res.registerAdvancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error is not None:
            return res

        if self.current_token.type != T_LBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '{'"))
        res.registerAdvancement()
        self.advance()
        expr = res.register(self.statements())
        if res.error is not None:
            return res

        if self.current_token.type != T_RBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
        res.registerAdvancement()
        self.advance()

        case.append((condition, expr))
        while self.current_token.match(T_KEYWORD, 'elif'):
            res.registerAdvancement()
            self.advance()
            condition = res.register(self.expr())
            if res.error is not None:
                return res

            if self.current_token.type != T_LBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '{'"))
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.statements())
            if res.error is not None:
                return res

            if self.current_token.type != T_RBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
            res.registerAdvancement()
            self.advance()

            case.append((condition, expr))

        if self.current_token.match(T_KEYWORD, 'else'):
            res.registerAdvancement()
            self.advance()
            if self.current_token.type != T_LBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '{'"))
            res.registerAdvancement()
            self.advance()
            else_case = res.register(self.statements())
            if res.error is not None:
                return res

            if self.current_token.type != T_RBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
            res.registerAdvancement()
            self.advance()

        return res.success(IfNode(case, else_case))

    def forExpr(self):
        '''
        for-expr -> KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr (KEYWORD:step expr)? LBRACE statements RBRACE
        '''
        res = ParserResult()

        if not self.current_token.match(T_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'for'"))
        res.registerAdvancement()
        self.advance()

        if self.current_token.type != T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier"))
        var_name = self.current_token
        res.registerAdvancement()
        self.advance()

        if self.current_token.type != T_EQ:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '='"))
        res.registerAdvancement()
        self.advance()
        start_value = res.register(self.expr())
        if res.error is not None:
            return res

        if not self.current_token.match(T_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'to'"))
        res.registerAdvancement()
        self.advance()
        end_value = res.register(self.expr())
        if res.error is not None:
            return res

        step_value = None
        if self.current_token.match(T_KEYWORD, 'step'):
            res.registerAdvancement()
            self.advance()
            step_value = res.register(self.expr())
            if res.error is not None:
                return res

        if self.current_token.type != T_LBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '{'"))
        res.registerAdvancement()
        self.advance()
        body = res.register(self.statements())
        if res.error is not None:
            return res

        if self.current_token.type != T_RBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
        res.registerAdvancement()
        self.advance()

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def whileExpr(self):
        '''
        while-expr -> KEYWORD:while expr LBRACE statements RBRACE
        '''
        res = ParserResult()

        if not self.current_token.match(T_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'while'"))
        res.registerAdvancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error is not None:
            return res

        if self.current_token.type != T_LBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '{'"))
        res.registerAdvancement()
        self.advance()
        body = res.register(self.statements())
        if res.error is not None:
            return res

        if self.current_token.type != T_RBRACE:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
        res.registerAdvancement()
        self.advance()

        return res.success(WhileNode(condition, body))

    def funcExpr(self):
        '''
        func-expr -> KEYWORD:func IDENTIFIER? LPAREN ( IDENTIFIER (COMMA IDENTIFIER)* )? RPAREN ARROW expr
                  -> KEYWORD:func IDENTIFIER? LPAREN ( IDENTIFIER (COMMA IDENTIFIER)* )? RPAREN ARROW LBRACE statements RBRACE
        '''
        res = ParserResult()

        if not self.current_token.match(T_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'func'"))
        res.registerAdvancement()
        self.advance()

        var_name = None
        if self.current_token.type == T_IDENTIFIER:
            var_name = self.current_token
            res.registerAdvancement()
            self.advance()

        if self.current_token.type != T_LPAREN:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '('"))
        res.registerAdvancement()
        self.advance()

        arg_name = []
        if self.current_token.type == T_IDENTIFIER:
            arg_name.append(self.current_token)
            res.registerAdvancement()
            self.advance()
            while self.current_token.type == T_COMMA:
                res.registerAdvancement()
                self.advance()
                if self.current_token.type != T_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier"))
                arg_name.append(self.current_token)
                res.registerAdvancement()
                self.advance()

        if self.current_token.type != T_RPAREN:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '('"))
        res.registerAdvancement()
        self.advance()

        if self.current_token.type != T_ARROW:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '->'"))
        res.registerAdvancement()
        self.advance()

        if self.current_token.type == T_LBRACE:
            res.registerAdvancement()
            self.advance()
            return_node = res.register(self.statements())
            if res.error is not None:
                return res

            if self.current_token.type != T_RBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
            res.registerAdvancement()
            self.advance()

            return res.success(FuncNode(var_name, arg_name, return_node, False))

        else:
            return_node = res.register(self.expr())
            if res.error is not None:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected int, float, identifier, '(' or '{'"))
            res.registerAdvancement()
            self.advance()

            return res.success(FuncNode(var_name, arg_name, return_node, True))

    def binOp(self, func_a, ops, func_b=None):
        # 递归调用，构建AST
        if func_b is None:
            func_b = func_a
        res = ParserResult()

        left = res.register(func_a())
        if res.error is not None:
            return res
        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            token = self.current_token
            res.registerAdvancement()
            self.advance()
            right = res.register(func_b())
            if res.error is not None:
                return res
            left = BinaryOpNode(left, token, right)
        return res.success(left)