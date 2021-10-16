#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from error import *
from symbol_table import *
import interpreter

import math

class Value(object):

    def __init__(self):
        self.setPos()
        self.setContext()

    def setPos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

# 数字
class Number(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value

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
                return None, RTError(num.pos_start, num.pos_end, 'Divisor cannot be 0', self.context)
            return Number(self.value / num.value).setContext(self.context), None

    def powBy(self, num):
        if isinstance(num, Number):
            return Number(self.value ** num.value).setContext(self.context), None

    def modBy(self, num):
        if isinstance(num, Number):
            if num.value == 0:
                return None, RTError(num.pos_start, num.pos_end, 'Divisor cannot be 0', self.context)
            return Number(self.value % num.value).setContext(self.context), None

    def compEE(self, num):
        if isinstance(num, Number):
            return Number(self.value == num.value).setContext(self.context), None

    def compNE(self, num):
        if isinstance(num, Number):
            return Number(self.value != num.value).setContext(self.context), None

    def compLT(self, num):
        if isinstance(num, Number):
            return Number(self.value < num.value).setContext(self.context), None

    def compGT(self, num):
        if isinstance(num, Number):
            return Number(self.value > num.value).setContext(self.context), None

    def compLTE(self, num):
        if isinstance(num, Number):
            return Number(self.value <= num.value).setContext(self.context), None

    def compGTE(self, num):
        if isinstance(num, Number):
            return Number(self.value >= num.value).setContext(self.context), None

    def logicAnd(self, num):
        if isinstance(num, Number):
            return Number(self.value and num.value).setContext(self.context), None

    def logicOr(self, num):
        if isinstance(num, Number):
            return Number(self.value or num.value).setContext(self.context), None

    def logicNot(self):
        return Number(not self.value).setContext(self.context), None

    def copy(self):
        return Number(self.value).setContext(self.context).setPos(self.pos_start, self.pos_end)

    def __repr__(self):
        return str(self.value)

# 内建变量
Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.PI = Number(math.pi)
Number.E = Number(math.e)

# 数组
class List(Value):

    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def __str__(self):
        return ', '.join([str(i) for i in self.elements])

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.elements])}]'

# 函数
class Function(Value):

    def __init__(self, name, arg_name, body_node, auto_return):
        super().__init__()
        self.name = name
        self.arg_name = arg_name
        self.body_node = body_node
        self.auto_return = auto_return

    def execute(self, args, itp):
        res = interpreter.RunResult()

        new_ctx = interpreter.Context(self.name, self.context, self.pos_start)
        new_ctx.symbol_table = SymbolTable(new_ctx.parent.symbol_table)

        if len(args) > len(self.arg_name):
            return res.failure(RTError(self.pos_start, self.pos_end, f'{len(args) - len(self.arg_name)} more arguments passed into {self.name}', self.context))
        elif len(args) < len(self.arg_name):
            return res.failure(RTError(self.pos_start, self.pos_end, f'{len(self.arg_name) - len(args)} fewer arguments passed into {self.name}', self.context))

        for i in range(len(args)):
            arg_name = self.arg_name[i]
            arg_value = args[i]
            arg_value.setContext(new_ctx)
            new_ctx.symbol_table.set(arg_name, arg_value)

        value = res.register(itp.visit(self.body_node, new_ctx))
        if res.shouldReturn() and res.func_return_value is None:
            return res
        return_value = (value if self.auto_return else None) or res.func_return_value or Number.null
        return res.success(return_value)

    def copy(self):
        return Function(self.name, self.arg_name, self.body_node, self.auto_return).setContext(self.context).setPos(self.pos_start, self.pos_end)

    def __repr__(self):
        return f'<function {self.name}>'