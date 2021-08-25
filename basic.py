#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 常量
DIGITS = '0123456789'

# 类型
T_INT = 'INT'
T_FLOAT = 'FLOAT'
T_PLUS = 'PLUS'
T_MINUS = 'MINUS'
T_MUL = 'MUL'
T_DIV = 'DIV'
T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'

class Error(object):

    def __init__(self, pos_start, pos_end, name, detail):
        '''
        @param pos_start 起始位置
        @param pos_end 结束位置
        @param name 错误类型
        @param detail 错误信息
        '''
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.name = name
        self.detail = detail

    def getError(self):
        res = f'{self.name}: {self.detail}\n'
        res += f'File {self.pos_start.file}, line {self.pos_end.ln + 1}'
        return res

# 非法字符错误
class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, detail):
        super().__init__(pos_start, pos_end, 'Illegal Character', detail)

class Token(object):

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}: {self.value}'
        return f'{self.type}'

class Position(object):

    def __init__(self, index, ln, col, file, text):
        '''
        @param index 索引
        @param ln 行号
        @param col 列号
        @param file 文件
        @param text 内容
        '''
        self.index = index
        self.ln = ln
        self.col = col
        self.file = file
        self.text = text

    def advance(self, current_char):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.col = 0
            self.ln += 1

    def copy(self):
        return Position(self.index, self.ln, self.col, self.file, self.text)

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
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(T_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(T_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(T_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(T_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(T_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(T_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        return tokens, None

    def make_number(self):
        num_str = ''
        dot = False

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
            return Token(T_INT, int(num_str))
        else:
            return Token(T_FLOAT, float(num_str))


def run(file, text):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    return tokens, err
