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