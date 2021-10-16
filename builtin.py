#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_type import Number
from symbol_table import SymbolTable

global_symbol_table = SymbolTable()
global_symbol_table.set('null', Number.null)
global_symbol_table.set('true', Number.true)
global_symbol_table.set('false', Number.false)
global_symbol_table.set('PI', Number.PI)
global_symbol_table.set('E', Number.E)