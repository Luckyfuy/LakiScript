#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import basic

while True:
    text = input('> ')
    res, err = basic.run('<stdin>', text)
    if err is not None:
        print(err.getError())
    else:
        print(res)