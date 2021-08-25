#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main

while True:
    text = input('> ')
    res, err = main.run('<stdin>', text)
    if err is not None:
        print(err.getError())
    else:
        print(res)