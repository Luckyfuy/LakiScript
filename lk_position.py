#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Position(object):

    def __init__(self, index, ln, col, file, text):
        '''
        @param index 索引
        @param ln 行号
        @param col 列号
        @param file 文件
        @param text 内容
        '''
        self.index = index
        self.ln = ln
        self.col = col
        self.file = file
        self.text = text

    def advance(self, current_char):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.col = 0
            self.ln += 1

    def copy(self):
        return Position(self.index, self.ln, self.col, self.file, self.text)