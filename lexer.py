#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from position import Position
from error import IllegalCharError

# 词法分析器
class Lexer(object):

    def __init__(self, file, text):
        self.file = file
        self.text = text
        self.pos = Position(-1, 0, -1, file, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.index < len(self.text):
            self.current_char = self.text[self.pos.index]
        else:
            self.current_char = None

    def makeTokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in (' ', '\t'):
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.makeNumber())
            elif self.current_char in LETTERS:
                tokens.append(self.makeIdentifier())
            elif self.current_char == '=':
                tokens.append(Token(T_EQ, pos_start=self.pos))
                self.advance()
            elif self.current_char == '+':
                tokens.append(Token(T_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(T_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(T_MUL, pos_start=self.pos))
                self.advance()
                if self.current_char == '*':
                    tokens[-1] = Token(T_POW, pos_start=self.pos)
                    self.advance()
            elif self.current_char == '/':
                tokens.append(Token(T_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(T_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(T_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        tokens.append(Token(T_EOF, pos_start=self.pos))
        return tokens, None

    def makeNumber(self):
        num_str = ''
        dot = False
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot:
                    break
                dot = True
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if not dot:
            return Token(T_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(T_FLOAT, float(num_str), pos_start, self.pos)

    def makeIdentifier(self):
        '''
        识别变量
        '''
        var_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            var_str += self.current_char
            self.advance()

        if var_str in KEYWORDS:
            token_type = T_KEYWORD
        else:
            token_type = T_IDENTIFIER
        return Token(token_type, var_str, pos_start, self.pos)