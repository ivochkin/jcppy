#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.cpp.type_ import Type
from jcppy.cpp.variable import Variable
from tests import _l, to_string


class TestVariable(unittest.TestCase):
    def setUp(self):
        self.decl = Variable(Type("int"), "foo")

    def test_plain(self):
        decl = to_string(self.decl)
        self.assertEqual(_l(decl), "int foo;\n")

    def test_pointer(self):
        self.decl.typ.pointer = True
        decl = to_string(self.decl)
        self.assertEqual(_l(decl), "int* foo;\n")

    def test_reference(self):
        self.decl.typ.reference = True
        decl = to_string(self.decl)
        self.assertEqual(_l(decl), "int& foo;\n")

    def test_const(self):
        self.decl.typ.const = True
        decl = to_string(self.decl)
        self.assertEqual(_l(decl), "const int foo;\n")

    def test_const_reference(self):
        self.decl.typ.reference = True
        self.decl.typ.const = True
        decl = to_string(self.decl)
        self.assertEqual(_l(decl), "const int& foo;\n")


if __name__ == "__main__":
    sys.exit(unittest.main())
