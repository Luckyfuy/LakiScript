#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string

# 常量
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

# 类型
T_INT = 'INT'
T_FLOAT = 'FLOAT'
T_PLUS = 'PLUS'
T_MINUS = 'MINUS'
T_MUL = 'MUL'
T_DIV = 'DIV'
T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_EOF = 'EOF' # 终止符
T_EQ = 'EQ'
T_POW = 'POW'
T_IDENTIFIER = 'IDENTIFIER'
T_KEYWORD = 'KEYWORD'

# 关键字
KEYWORDS = (
    'var',
)

class Token(object):

    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        if pos_start is not None:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(self.value)
        if pos_end is not None:
            self.pos_end = pos_end

    def match(self, type_, value):
        '''
        判断Token是否相同
        '''
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}: {self.value}'
        return f'{self.type}'