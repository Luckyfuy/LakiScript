#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lexer import *
from lk_parser import *

def run(file, text):
    lexer = Lexer(file, text)
    tokens, err = lexer.makeTokens()
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error