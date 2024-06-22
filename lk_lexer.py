#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from lk_position import Position
from lk_error import IllegalCharError, ExpectedCharError

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
            elif self.current_char == '\'':
                tokens.append(self.makeString())
            elif self.current_char == '=':
                tokens.append(self.makeEqual())
            elif self.current_char == '<':
                tokens.append(self.makeLessThan())
            elif self.current_char == '>':
                tokens.append(self.makeGreaterThan())
            elif self.current_char == '!':
                token, err = self.makeNotEqual()
                if err is not None:
                    return [], err
                tokens.append(token)
            elif self.current_char == '+':
                tokens.append(self.makePlus())
            elif self.current_char == '-':
                tokens.append(self.makeMinus())
            elif self.current_char == '*':
                tokens.append(self.makeAsterisk())
            elif self.current_char == '/':
                self.advance()
                if self.current_char == '/':
                    self.skipComment()
                elif self.current_char == '=':
                    tokens.append(Token(T_DIVEQ, pos_start=self.pos))
                    self.advance()
                else:
                    tokens.append(Token(T_DIV, pos_start=self.pos))
            elif self.current_char == '%':
                tokens.append(self.makeMod())
            elif self.current_char == '(':
                tokens.append(Token(T_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(T_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(T_LBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(T_RBRACE, pos_start=self.pos))
                tokens.append(Token(T_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(T_LBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(T_RBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(T_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char in ';\n':
                tokens.append(Token(T_NEWLINE, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        tokens.append(Token(T_EOF, pos_start=self.pos))
        return tokens, None

    def skipComment(self):
        self.advance()
        while self.current_char != '\n':
            self.advance()
        self.advance()

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

    def makeString(self):
        string = ''
        pos_start = self.pos.copy()
        escape_char = False
        escape_chars = {
            'n': '\n',
            't': '\t'
        }

        self.advance()
        while self.current_char is not None and (self.current_char != '\'' or escape_char):
            if escape_char:
                string += escape_chars.get(self.current_char, self.current_char)
                escape_char = False
            else:
                if self.current_char == '\\':
                    escape_char = True
                else:
                    string += self.current_char
            self.advance()

        self.advance()
        return Token(T_STRING, string, pos_start, self.pos)

    def makeIdentifier(self):
        '''
        匹配关键字或变量名
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

    def makePlus(self):
        '''
        匹配+或+=
        '''
        token_type = T_PLUS
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_PLUSEQ
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeMinus(self):
        '''
        匹配-或-=或->
        '''
        token_type = T_MINUS
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_MINUSEQ
        elif self.current_char == '>':
            self.advance()
            token_type = T_ARROW
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeAsterisk(self):
        '''
        匹配*或**或*=或**=
        '''
        token_type = T_MUL
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '*':
            self.advance()
            token_type = T_POW
            if self.current_char == '=':
                self.advance()
                token_type = T_POWEQ
        elif self.current_char == '=':
            self.advance()
            token_type = T_MULEQ
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeMod(self):
        '''
        匹配%或%=
        '''
        token_type = T_MOD
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_MODEQ
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeEqual(self):
        '''
        匹配=或==
        '''
        token_type = T_EQ
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_EE
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeLessThan(self):
        '''
        匹配<或<=
        '''
        token_type = T_LT
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_LTE
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeGreaterThan(self):
        '''
        匹配>或>=
        '''
        token_type = T_GT
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_GTE
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeNotEqual(self):
        '''
        匹配!=
        不匹配单独的!
        '''
        pos_start = self.pos.copy()

        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(T_NE, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "The character after '!' should be '='")