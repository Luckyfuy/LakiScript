#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from error import *

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

# 数组
class List(Value):

    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def __str__(self):
        return ', '.join([str(i) for i in self.elements])

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.elements])}]'