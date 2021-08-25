#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
AST节点
'''

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