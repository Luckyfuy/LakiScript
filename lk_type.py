#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_error import *
from lk_symbol_table import *
import lk_interpreter

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

    def illegalOperation(self, other=None):
        if other is None:
            other = self
        return RTError(self.pos_start, other.pos_end, 'Illegal Operation', self.context)

# 数字
class Number(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def addBy(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def subBy(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def mulBy(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context), None
        elif isinstance(other, String):
            return String(self.value * other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def divBy(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Divisor cannot be 0', self.context)
            return Number(self.value / other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def powBy(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def modBy(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Divisor cannot be 0', self.context)
            return Number(self.value % other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compEE(self, other):
        if isinstance(other, Number):
            return Number(self.value == other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compNE(self, other):
        if isinstance(other, Number):
            return Number(self.value != other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compLT(self, other):
        if isinstance(other, Number):
            return Number(self.value < other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compGT(self, other):
        if isinstance(other, Number):
            return Number(self.value > other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compLTE(self, other):
        if isinstance(other, Number):
            return Number(self.value <= other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compGTE(self, other):
        if isinstance(other, Number):
            return Number(self.value >= other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def logicAnd(self, other):
        if isinstance(other, Number):
            return Number(self.value and other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def logicOr(self, other):
        if isinstance(other, Number):
            return Number(self.value or other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

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

# 字符串
class String(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def addBy(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def mulBy(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compEE(self, other):
        if isinstance(other, String):
            return Number(self.value == other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compNE(self, other):
        if isinstance(other, String):
            return Number(self.value != other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def copy(self):
        return String(self.value).setContext(self.context).setPos(self.pos_start, self.pos_end)

    def __repr__(self):
        return f'\'{self.value}\''

# 数组
class List(Value):

    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def addBy(self, other):
        if isinstance(other, List):
            return List(self.elements + other.elements).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def mulBy(self, other):
        if isinstance(other, Number):
            return List(self.elements * other.value).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compEE(self, other):
        if isinstance(other, List):
            return Number(self.elements == other.elements).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def compNE(self, other):
        if isinstance(other, List):
            return Number(self.elements != other.elements).setContext(self.context), None
        else:
            return None, self.illegalOperation(other)

    def copy(self):
        return List(self.elements).setContext(self.context).setPos(self.pos_start, self.pos_end)

    def __str__(self):
        return ', '.join([str(i) for i in self.elements])

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.elements])}]'

# 函数
class Function(Value):

    def __init__(self, name, arg_name, body_node, auto_return):
        super().__init__()
        self.name = name or '<anonymous>'
        self.arg_name = arg_name
        self.body_node = body_node
        self.auto_return = auto_return

    def execute(self, args, itp):
        res = lk_interpreter.RunResult()

        new_ctx = lk_interpreter.Context(self.name, self.context, self.pos_start)
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

# 内建函数
class BuiltinFunction(Function):

    def __init__(self, name):
        super().__init__(name, None, None, None)

    def execute(self, args, _):
        res = lk_interpreter.RunResult()

        new_ctx = lk_interpreter.Context(self.name, self.context, self.pos_start)
        new_ctx.symbol_table = SymbolTable()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.noExecuteMethod)

        if len(args) > len(method.arg_name):
            return res.failure(RTError(self.pos_start, self.pos_end, f'{len(args) - len(method.arg_name)} more arguments passed into {self.name}', self.context))
        elif len(args) < len(method.arg_name):
            return res.failure(RTError(self.pos_start, self.pos_end, f'{len(method.arg_name) - len(args)} fewer arguments passed into {self.name}', self.context))

        for i in range(len(args)):
            arg_name = method.arg_name[i]
            arg_value = args[i]
            arg_value.setContext(new_ctx)
            new_ctx.symbol_table.set(arg_name, arg_value)

        return_value = res.register(method(new_ctx))
        if res.shouldReturn():
            return res
        return res.success(return_value)

    def noExecuteMethod(self, node, context):
        raise Exception(f'No execute_{self.name}')

    def copy(self):
        return BuiltinFunction(self.name).setContext(self.context).setPos(self.pos_start, self.pos_end)

    def __repr__(self):
        return f'<built-in function {self.name}>'



    def execute_print(self, ctx):
        print(ctx.symbol_table.get('value').value)
        return lk_interpreter.RunResult().success(Number.null)
    execute_print.arg_name = ['value']

    def execute_input(self, ctx):
        return lk_interpreter.RunResult().success(String(input()))
    execute_input.arg_name = []

    def execute_int(self, ctx):
        value = ctx.symbol_table.get('value')
        try:
            return lk_interpreter.RunResult().success(Number(int(value.value)))
        except ValueError:
            return lk_interpreter.RunResult().failure(RTError(value.pos_start, value.pos_end, f'{value} cannot be converted to an int', value.context))
    execute_int.arg_name = ['value']

    def execute_str(self, ctx):
        return lk_interpreter.RunResult().success(String(str(ctx.symbol_table.get('value').value)))
    execute_str.arg_name = ['value']

BuiltinFunction.print = BuiltinFunction('print')
BuiltinFunction.input = BuiltinFunction('input')
BuiltinFunction.int = BuiltinFunction('int')
BuiltinFunction.str = BuiltinFunction('str')