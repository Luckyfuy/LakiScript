#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from lk_type import *
from ast_node import VarAccessNode, VarAssignNode, BinaryOpNode
from error import RTError

# 运行结果
class RunResult(object):

    def __init__(self):
        self.value = None
        self.error = None

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

    def register(self, res):
        if res.error is not None:
            self.error = res.error
        return res.value

# 上下文
class Context(object):

    def __init__(self, name, parent=None, parent_pos=None):
        self.name = name
        self.parent = parent
        self.parent_pos = parent_pos
        self.symbol_table = None

# 解释器
class Interpreter(object):

    def visit(self, node, context):
        '''
        遍历AST节点
        @param node 起始节点
        @param context 上下文
        '''
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.noVisitMethod)
        return method(node, context)

    def noVisitMethod(self, node, context):
        raise Exception(f'No visit_{type(node).__name__}')

    def visit_NumberNode(self, node, context):
        return RunResult().success(Number(node.token.value).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RunResult()
        elements = []

        for i in node.element_nodes:
            elements.append(res.register(self.visit(i, context)))
            if res.error is not None:
                return res

        return res.success(List(elements).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RunResult()
        var_name = node.name_token.value
        value = context.symbol_table.get(var_name)
        if value is None:
            return res.failure(RTError(node.pos_start, node.pos_end, f'{var_name} is undefined', context))
        value = value.copy().setPos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RunResult()
        var_name = node.name_token.value
        if not node.define:
            org_value = context.symbol_table.get(var_name)
            if org_value is None:
                return res.failure(RTError(node.pos_start, node.pos_end, f'{var_name} is undefined', context))
        if node.eq == T_PLUSEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_PLUS), node.value_node), T_EQ), context)
        elif node.eq == T_MINUSEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_MINUS), node.value_node), T_EQ), context)
        elif node.eq == T_MULEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_MUL), node.value_node), T_EQ), context)
        elif node.eq == T_DIVEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_DIV), node.value_node), T_EQ), context)
        elif node.eq == T_POWEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_POW), node.value_node), T_EQ), context)
        value = res.register(self.visit(node.value_node, context))
        if res.error is not None:
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinaryOpNode(self, node, context):
        res = RunResult()

        left = res.register(self.visit(node.lnode, context))
        if res.error is not None:
            return res
        right = res.register(self.visit(node.rnode, context))
        if res.error is not None:
            return res

        if node.token.type == T_PLUS:
            result, err = left.addBy(right)
        elif node.token.type == T_MINUS:
            result, err = left.subBy(right)
        elif node.token.type == T_MUL:
            result, err = left.mulBy(right)
        elif node.token.type == T_DIV:
            result, err = left.divBy(right)
        elif node.token.type == T_POW:
            result, err = left.powBy(right)
        elif node.token.type == T_EE:
            result, err = left.compEE(right)
        elif node.token.type == T_NE:
            result, err = left.compNE(right)
        elif node.token.type == T_LT:
            result, err = left.compLT(right)
        elif node.token.type == T_GT:
            result, err = left.compGT(right)
        elif node.token.type == T_LTE:
            result, err = left.compLTE(right)
        elif node.token.type == T_GTE:
            result, err = left.compGTE(right)
        elif node.token.match(T_KEYWORD, 'and'):
            result, err = left.logicAnd(right)
        elif node.token.match(T_KEYWORD, 'or'):
            result, err = left.logicOr(right)
        else:
            return res.failure(RTError(node.pos_start, node.pos_end, f'{node.token.type} is not supported', context))

        if err is not None:
            return res.failure(err)
        return res.success(result.setPos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RunResult()
        num = res.register(self.visit(node.node, context))
        if res.error is not None:
            return res

        err = None
        if node.token.type == T_MINUS:
            num, err = num.mulBy(Number(-1))
        elif node.token.match(T_KEYWORD, 'not'):
            num, err = num.logicNot()

        if err is not None:
            return res.failure(err)
        return res.success(num.setPos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RunResult()

        for condition, expr in node.case:
            condition_value = res.register(self.visit(condition, context))
            if res.error is not None:
                return res

            if condition_value.value:
                expr_value = res.register(self.visit(expr, context))
                if res.error is not None:
                    return res
                return res.success(expr_value)

        if node.else_case is not None:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error is not None:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RunResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error is not None:
                return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error is not None:
                return res

        step_value = Number(1)
        if node.step_value_node is not None:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error is not None:
                return res

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i <= end_value.value
        else:
            condition = lambda: i >= end_value.value

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value
            res.register(self.visit(node.body_node, context))
            if res.error is not None:
                return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RunResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error is not None:
                return res
            if not condition.value:
                break

            res.register(self.visit(node.body_node, context))
            if res.error is not None:
                return res

        return res.success(None)