#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lexer import Lexer
from lk_parser import Parser
from interpreter import Interpreter, Context

def run(file, text):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    print(tokens)

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    context = Context('<program>')
    res = interpreter.visit(ast.node, context)
    return res.value, res.error