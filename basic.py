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
T_EOF = 'EOF' # 终止符

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

# 非法字符
class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, detail):
        super().__init__(pos_start, pos_end, 'Illegal Character', detail)

# 无效语法
class InvalidSyntaxError(Error):

    def __init__(self, pos_start, pos_end, detail):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', detail)

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
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(T_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(T_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(T_MUL, pos_start=self.pos))
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

# AST节点
# 数字节点
class NumberNode(object):

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

# 二元操作符节点
# + - * /
class BinaryOpNode(object):

    def __init__(self, lnode, token, rnode):
        self.lnode = lnode
        self.token = token
        self.rnode = rnode

    def __repr__(self):
        return f'({self.lnode}, {self.token}, {self.rnode})'

# 一元操作符节点
# 负号-
class UnaryOpNode(object):

    def __init__(self, token, node):
        self.token = token
        self.node = node

    def __repr__(self):
        return f'({self.token}, {self.node})'

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


def run(file, text):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error