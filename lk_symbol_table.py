#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
符号表
'''

class SymbolTable(object):

    def __init__(self, parent=None):
        # 符号表
        self.symbols = {}
        # 作用域
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent is not None:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]