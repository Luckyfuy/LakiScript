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

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

    def register(self, res):
        if isinstance(res, ParserResult):
            if res.error is not None:
                self.error = res.error
            return res.node
        return res

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

    '''
    BNF
    expr -> term (( PLUS | MINUS ) term)*
    term -> factor ( MUL | DIV ) factor)*
    factor -> INT | FLOAT
           -> (PLUS | MINUS) factor
           -> LPAREN expr RPAREN
    '''
    def parse(self):
        res = self.expr()
        if res.error is None and self.current_token.type != T_EOF:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' or '/'"))
        return res

    def factor(self):
        '''
        factor -> INT | FLOAT
               -> (PLUS | MINUS) factor
               -> LPAREN expr RPAREN
        '''
        res = ParserResult()
        token = self.current_token

        if token.type in (T_INT, T_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(token))

        elif token.type in (T_PLUS, T_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error is not None:
                return res
            return res.success(UnaryOpNode(token, factor))

        elif token.type == T_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error is not None:
                return res
            if self.current_token.type == T_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ')'"))
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected int or float"))

    def term(self):
        # term -> factor ( MUL | DIV ) factor)*
        return self.binOp(self.factor, (T_MUL, T_DIV))

    def expr(self):
        # expr -> term (( PLUS | MINUS ) term)*
        return self.binOp(self.term, (T_PLUS, T_MINUS))

    def binOp(self, func, ops):
        # 递归调用，构建AST
        res = ParserResult()
        left = res.register(func())
        while self.current_token.type in ops:
            token = self.current_token
            res.register(self.advance())
            right = res.register(func())
            left = BinaryOpNode(left, token, right)
        return res.success(left)