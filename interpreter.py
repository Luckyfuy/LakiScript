#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from error import RuntimeError

# 运行结果
class RunResult(object):

    def __init__(self):
        self.value = None
        self.error = None

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

    def register(self, res):
        if res.error is not None:
            self.error = res.error
        return res.value

# 数字
class Number(object):

    def __init__(self, value):
        self.value = value
        self.setPos()
        self.setContext()

    def setPos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def addBy(self, num):
        if isinstance(num, Number):
            return Number(self.value + num.value).setContext(self.context), None

    def subBy(self, num):
        if isinstance(num, Number):
            return Number(self.value - num.value).setContext(self.context), None

    def mulBy(self, num):
        if isinstance(num, Number):
            return Number(self.value * num.value).setContext(self.context), None

    def divBy(self, num):
        if isinstance(num, Number):
            if num.value == 0:
                return None, RuntimeError(num.pos_start, num.pos_end, 'Divisor cannot be 0', self.context)
            return Number(self.value / num.value).setContext(self.context), None

    def __repr__(self):
        return str(self.value)

# 上下文
class Context(object):

    def __init__(self, name, parent=None, parent_pos=None):
        self.name = name
        self.parent = parent
        self.parent_pos = parent_pos

# 解释器
class Interpreter(object):

    def visit(self, node, context):
        '''
        遍历AST节点
        @param node 起始节点
        @param context 上下文
        '''
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.noVisitMethod)
        return method(node, context)

    def noVisitMethod(self):
        raise Exception(f'No visit_{type(node).__name__}')

    def visit_NumberNode(self, node, context):
        return RunResult().success(Number(node.token.value).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_BinaryOpNode(self, node, context):
        res = RunResult()

        left = res.register(self.visit(node.lnode, context))
        if res.error is not None:
            return res
        right = res.register(self.visit(node.rnode, context))
        if res.error is not None:
            return res

        if node.token.type == T_PLUS:
            result, err = left.addBy(right)
        elif node.token.type == T_MINUS:
            result, err = left.subBy(right)
        elif node.token.type == T_MUL:
            result, err = left.mulBy(right)
        elif node.token.type == T_DIV:
            result, err = left.divBy(right)

        if err is not None:
            return res.failure(err)
        return res.success(result.setPos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RunResult()
        num = res.register(self.visit(node.node, context))
        if res.error is not None:
            return res

        err = None
        if node.token.type == T_MINUS:
            num, err = num.mulBy(Number(-1))

        if err is not None:
            return res.failure(err)
        return res.success(num.setPos(node.pos_start, node.pos_end))