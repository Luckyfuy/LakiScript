#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lexer import Lexer
from lk_parser import Parser
from interpreter import Interpreter, Context, Number
from symbol_table import SymbolTable

# 全局作用域
global_symbol_table = SymbolTable()
global_symbol_table.set('True', Number(1))
global_symbol_table.set('False', Number(0))

def run(file, text, debug=False):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    if debug:
        if err is not None:
            print(err.getError())
        else:
            print(tokens)

    parser = Parser(tokens)
    ast = parser.parse()
    if debug:
        if ast.error is not None:
            print(ast.error.getError())
        else:
            print(ast.node)

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    res = interpreter.visit(ast.node, context)
    return res.value, res.error