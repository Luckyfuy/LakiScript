#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lexer import Lexer
from lk_parser import Parser
from interpreter import Interpreter, Context
from builtin import global_symbol_table

def run(file, text, debug=False):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    if err is not None:
        return None, err
    if debug:
        print(tokens)

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:
        return None, ast.error
    if debug:
        print(ast.node)

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    res = interpreter.visit(ast.node, context)

    return res.value, res.error