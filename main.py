#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_lexer import Lexer
from lk_parser import Parser
from lk_interpreter import Interpreter, Context
from lk_builtin import global_symbol_table

import sys

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
    # if debug:
    #     print(ast.node)

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    res = interpreter.visit(ast.node, context)

    return res.value, res.error

def shell():
    print('LakiScript Shell')
    print()

    while True:
        text = input('> ')
        res, err = run('<stdin>', text, debug=True)
        if err is not None:
            print(err.getError())
        else:
            print(res)

def runFile(file_path):
    try:
        with open(file_path, 'r', encoding='UTF-8') as f:
            script = f.read()
    except Exception as e:
        print(f'Fail to load script {file_path}, error: {e}')
        raise

    res, err = run(file_path, script, debug=False)
    if err is not None:
        print(err.getError())
    # else:
    #     print(res)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        runFile(file_path)
    else:
        shell()