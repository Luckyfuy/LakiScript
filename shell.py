#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import main

def shell():
    print('LakiScript Shell')
    print()

    while True:
        text = input('> ')
        res, err = main.run('<stdin>', text, debug=True)
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

    res, err = main.run(file_path, script, debug=True)
    if err is not None:
            print(err.getError())
    else:
        print(res)

if len(sys.argv) > 1:
    file_path = sys.argv[1]
    runFile(file_path)
else:
    shell()