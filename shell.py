#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main

print('LakiScript Shell')
print()

while True:
    text = input('> ')
    res, err = main.run('<stdin>', text, debug=True)
    if err is not None:
        print(err.getError())
    else:
        print(res)