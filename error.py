#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
错误
'''

class Error(object):

    def __init__(self, pos_start, pos_end, name, detail):
        '''
        @param pos_start 起始位置
        @param pos_end 结束位置
        @param name 错误类型
        @param detail 错误信息
        '''
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.name = name
        self.detail = detail

    def getError(self):
        res = f'{self.name}: {self.detail}\n'
        res += f'File {self.pos_start.file}, line {self.pos_end.ln + 1}'
        return res

# 非法字符
class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, detail):
        super().__init__(pos_start, pos_end, 'Illegal Character', detail)

# 无效语法
class InvalidSyntaxError(Error):

    def __init__(self, pos_start, pos_end, detail):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', detail)