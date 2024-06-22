#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lk_token import *
from lk_type import *
from lk_ast_node import VarAccessNode, VarAssignNode, BinaryOpNode
from lk_error import RTError

# 运行结果
class RunResult(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def successReturn(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def successContinue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def successBreak(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def register(self, res):
        if res.error is not None:
            self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def shouldReturn(self, only_err=False):
        if only_err:
            return self.error is not None or self.func_return_value is not None
        else:
            return self.error is not None or self.func_return_value is not None or self.loop_should_continue or self.loop_should_break

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

    def visit_StringNode(self, node, context):
        return RunResult().success(String(node.token.value).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RunResult()
        elements = []

        for i in node.element_nodes:
            elements.append(res.register(self.visit(i, context)))
            if res.shouldReturn():
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
        elif node.eq == T_MODEQ:
            return self.visit(VarAssignNode(node.name_token, BinaryOpNode(VarAccessNode(node.name_token), Token(T_MOD), node.value_node), T_EQ), context)
        value = res.register(self.visit(node.value_node, context))
        if res.shouldReturn():
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinaryOpNode(self, node, context):
        res = RunResult()

        left = res.register(self.visit(node.lnode, context))
        if res.shouldReturn():
            return res
        right = res.register(self.visit(node.rnode, context))
        if res.shouldReturn():
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
        elif node.token.type == T_MOD:
            result, err = left.modBy(right)
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
        if res.shouldReturn():
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
            if res.shouldReturn():
                return res

            if condition_value.value:
                expr_value = res.register(self.visit(expr, context))
                if res.shouldReturn():
                    return res
                return res.success(expr_value)

        if node.else_case is not None:
            else_value = res.register(self.visit(node.else_case, context))
            if res.shouldReturn():
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RunResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.shouldReturn():
                return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.shouldReturn():
                return res

        step_value = Number(1)
        if node.step_value_node is not None:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.shouldReturn():
                return res

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i <= end_value.value
        else:
            condition = lambda: i >= end_value.value

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value
            value = res.register(self.visit(node.body_node, context))
            if res.shouldReturn(True):
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(List(elements).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RunResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.shouldReturn():
                return res
            if not condition.value:
                break

            value = res.register(self.visit(node.body_node, context))
            if res.shouldReturn(True):
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(List(elements).setContext(context).setPos(node.pos_start, node.pos_end))

    def visit_FuncNode(self, node, context):
        res = RunResult()

        func_name = node.name_token.value if node.name_token is not None else None
        arg_name = [arg.value for arg in node.arg_name_tokens]
        body_node = node.body_node

        func_value = Function(func_name, arg_name, body_node, node.auto_return).setContext(context).setPos(node.pos_start, node.pos_end)

        if node.name_token is not None:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RunResult()
        args = []

        value = res.register(self.visit(node.func_node, context))
        if res.shouldReturn():
            return res
        value = value.copy().setPos(node.pos_start, node.pos_end)

        for arg in node.arg_nodes:
            args.append(res.register(self.visit(arg, context)))
            if res.shouldReturn():
                return res

        return_value = res.register(value.execute(args, self))
        if res.shouldReturn():
            return res
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RunResult()

        value = Number.null
        if node.node is not None:
            value = res.register(self.visit(node.node, context))
            if res.shouldReturn():
                return res
        return res.successReturn(value)

    def visit_ContinueNode(self, node, context):
        res = RunResult()

        return res.successContinue()

    def visit_BreakNode(self, node, context):
        res = RunResult()

        return res.successBreak()