#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.builder import build
from jcppy.cpp.config import Config
from jcppy.cpp.function import Function
from jcppy.cpp.type_ import Type
from jcppy.cpp.variable import Variable
from tests import _l, to_string

def decl_to_string(func):
    return to_string(func, func.write_declaration)


class TestFunctionNaming(unittest.TestCase):
    def setUp(self):
        self.func = Function("create.object")

    def test_default(self):
        decl = decl_to_string(self.func)
        self.assertEqual(_l(decl), "void createObject();\n")

    def test_tricky(self):
        self.func.config.naming.function = "pascal"
        self.func.config.naming.function_prefix = "f_"
        self.func.config.naming.function_suffix = "_"
        decl = decl_to_string(self.func)
        self.assertEqual(_l(decl), "void f_CreateObject_();\n")


class TestFunctionLineWidthAdjustment(unittest.TestCase):
    def setUp(self):
        self.func = Function("make.struct")
        self.func.returns = Type("int")
        self.func.args.append(Variable(build(Type, "void").pointer(True).wrap(), "bar"))
        self.func.args.append(Variable(build(Type, "boost::uuids::uuid").const(True).reference(True).wrap(), "id"))

    def test_oneline(self):
        self.func.config.linewidth = 80
        decl = decl_to_string(self.func)
        self.assertEqual(_l(decl),
                         "int makeStruct(void* bar, const boost::uuids::uuid& id);\n")

    def test_arg_on_each_line(self):
        self.func.config.linewidth = 10
        self.func.config.indent.function_declaration = 1
        self.func.config.indent.symbol = "\t"
        decl = decl_to_string(self.func)
        self.assertEqual(_l(decl),
                         "int makeStruct(\n\tvoid* bar,\n\tconst boost::uuids::uuid& id);\n")


class TestFunctionSpecifiers(unittest.TestCase):
    def setUp(self):
        self.func = Function("add.value")
        self.func.returns = build(Type, "int").pointer(True).wrap()
        self.func.args.append(Variable(Type("int"), "lhs"))
        self.func.args.append(Variable(Type("int"), "rhs"))

    def test_static(self):
        self.func.config.naming.function = "c"
        self.func.config.naming.function_prefix = "g_"
        self.func.config.naming.function_suffix = ""
        self.func.static = True
        decl = decl_to_string(self.func)
        self.assertEqual(_l(decl),
                         "static int* g_add_value(int lhs, int rhs);\n")


if __name__ == "__main__":
    sys.exit(unittest.main())
