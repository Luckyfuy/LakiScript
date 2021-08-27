#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from error import InvalidSyntaxError
from ast_node import *

# 语法解析结果
class ParserResult(object):

    def __init__(self):
        self.error = None
        self.node = None
        self.advance_cnt = 0

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

    def parse(self):
        res = self.expr()
        if res.error is None and self.current_token.type != T_EOF:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' or '/'"))
        return res

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
        return self.binOp(self.atom, (T_POW, ), self.factor)

    def atom(self):
        res = ParserResult()
        token = self.current_token

        if token.type in (T_INT, T_FLOAT):
            res.registerAdvancement()
            self.advance()
            return res.success(NumberNode(token))

        elif token.type == T_IDENTIFIER:
            res.registerAdvancement()
            self.advance()
            return res.success(VarAccessNode(token))

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

        return res.failure(InvalidSyntaxError(token.pos_start, token.pos_end, "Expected int, float, identifier or '('"))


    def term(self):
        '''
        term -> factor (( MUL | DIV ) factor)*
        '''
        return self.binOp(self.factor, (T_MUL, T_DIV))

    def expr(self):
        '''
        expr -> KEYWORD: var IDENTIFIER EQ expr
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
            return res.success(VarAssignNode(var_name, expr))

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
        return self.binOp(self.term, (T_PLUS, T_MINUS))

    def ifExpr(self):
        '''
        if-expr -> KEYWORD: if expr { expr* }
                   ( KEYWORD: elif expr { expr* } )*
                   ( KEYWORD: else { expr* } )?
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
        expr = res.register(self.expr())
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
            expr = res.register(self.expr())
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
            else_case = res.register(self.expr())
            if res.error is not None:
                return res

            if self.current_token.type != T_RBRACE:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '}'"))
            res.registerAdvancement()
            self.advance()

        return res.success(IfNode(case, else_case))

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