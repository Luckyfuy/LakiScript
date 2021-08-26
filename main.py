#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lexer import Lexer
from lk_parser import Parser
from interpreter import Interpreter, Context

def run(file, text):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    if err is not None:
        print(err.getError())
    else:
        print(tokens)

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:
        print(ast.error.getError())
    else:
        print(ast.node)

    interpreter = Interpreter()
    context = Context('<program>')
    res = interpreter.visit(ast.node, context)
    return res.value, res.error