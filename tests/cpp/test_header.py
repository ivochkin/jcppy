#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.cpp.header import Header
from jcppy.cpp.function import Function
from jcppy.cpp.struct import Class
from jcppy.cpp.namespace import Namespace, make_namespace
from jcppy.cpp.include import Include
from jcppy.builder import build
from tests import _l, to_string


class TestHeader(unittest.TestCase):
    def setUp(self):
        self.header = Header("foo.h")
        self.header.functions.append(build(Function, "foo").wrap())
        self.header.classes.append(build(Class, "bar").wrap())

    def test_glob_function_and_class(self):
        self.header.pragma_once = False
        self.header.include_guard = False
        self.assertEqual(_l(to_string(self.header)),
"""\
/// @file foo.h
/// @warning Generated by jcppy, not intended for editing
/// @copyright The MIT License (MIT)

void foo();

class Bar {
};
""")

    def test_pragma_once(self):
        self.header.name = "foo/bar.h"
        self.header.pragma_once = True
        self.header.include_guard = True
        self.assertEqual(_l(to_string(self.header)),
"""\
/// @file foo/bar.h
/// @warning Generated by jcppy, not intended for editing
/// @copyright The MIT License (MIT)

#pragma once
#ifndef FOO_BAR_H_
#define FOO_BAR_H_

void foo();

class Bar {
};

#endif // FOO_BAR_H_
""")


if __name__ == "__main__":
    sys.exit(unittest.main())
