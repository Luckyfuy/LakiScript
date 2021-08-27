#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
AST节点
'''

# 数字节点
class NumberNode(object):

    def __init__(self, token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f'{self.token}'

# 访问变量
class VarAccessNode(object):

    def __init__(self, name_token):
        self.name_token = name_token
        self.pos_start = name_token.pos_start
        self.pos_end = name_token.pos_end

    def __repr__(self):
        return f'({self.name_token})'

# 定义变量
class VarAssignNode(object):

    def __init__(self, name_token, value_node):
        self.name_token = name_token
        self.value_node = value_node
        self.pos_start = name_token.pos_start
        self.pos_end = name_token.pos_end

    def __repr__(self):
        return f'({self.name_token}, {self.value_node})'

# 二元操作符节点
# + - * /
class BinaryOpNode(object):

    def __init__(self, lnode, token, rnode):
        self.lnode = lnode
        self.token = token
        self.rnode = rnode
        self.pos_start = lnode.pos_start
        self.pos_end = rnode.pos_end

    def __repr__(self):
        return f'({self.lnode}, {self.token}, {self.rnode})'

# 一元操作符节点
# 负号-
class UnaryOpNode(object):

    def __init__(self, token, node):
        self.token = token
        self.node = node
        self.pos_start = token.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.token}, {self.node})'

class IfNode(object):

    def __init__(self, case, else_case):
        self.case = case
        self.else_case = else_case
        self.pos_start = case[0][0].pos_start
        self.pos_end = (else_case or case[-1][0]).pos_end

    def __repr__(self):
        result = ''
        condition, expr = self.case[0]
        result += f'    if {condition} then {expr}\n'
        for condition, expr in self.case[1:]:
            result += f'    elif {condition} then {expr}\n'
        if self.else_case is not None:
            result += f'    else {self.else_case}\n'
        return f'(\n{result})'