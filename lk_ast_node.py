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

# 字符串节点
class StringNode(object):

    def __init__(self, token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f'{self.token}'

# 数组节点
class ListNode(object):

    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

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

    def __init__(self, name_token, value_node, eq, define=True):
        self.name_token = name_token
        self.value_node = value_node
        self.pos_start = name_token.pos_start
        self.pos_end = name_token.pos_end
        self.eq = eq
        self.define = define

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

# if条件语句
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

# for循环
class ForNode(object):

    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.pos_start = var_name_token.pos_start
        self.pos_end = body_node.pos_end

    def __repr__(self):
        result = f'(\nfor {self.var_name_token} = {self.start_value_node} to {self.end_value_node} step {self.step_value_node}\n'
        result += f'then {self.body_node}\n)'
        return result

# while循环
class WhileNode(object):

    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node
        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end

    def __repr__(self):
        result = f'(\nwhile {self.condition_node}\n'
        result += f'then {self.body_node}\n)'
        return result

# 定义函数
class FuncNode(object):

    def __init__(self, name_token, arg_name_tokens, body_node, auto_return):
        self.name_token = name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node
        self.auto_return = auto_return

        if name_token is not None:
            self.pos_start = name_token.pos_start
        elif len(arg_name_tokens) > 0:
            self.pos_start = arg_name_tokens[0].pos_start
        else:
            self.pos_start = body_node.pos_start
        self.pos_end = body_node.pos_end

# 调用函数
class CallNode(object):

    def __init__(self, func_node, arg_nodes):
        self.func_node = func_node
        self.arg_nodes = arg_nodes

        self.pos_start = func_node.pos_start
        if len(arg_nodes) > 0:
            self.pos_end = arg_nodes[-1].pos_end
        else:
            self.pos_end = func_node.pos_end

# return
class ReturnNode(object):

    def __init__(self, node, pos_start, pos_end):
        self.node = node
        self.pos_start = pos_start
        self.pos_end = pos_end

# continue
class ContinueNode(object):

    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

# break
class BreakNode(object):

    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end