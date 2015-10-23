#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.cpp.include import Include
from tests import _l, to_string


class TestInclude(unittest.TestCase):
    def test_contructor(self):
        inc1 = Include("foobar")
        inc2 = Include("foobar", brackets=True)
        inc3 = Include("foobar", quotes=True)
        self.assertFalse(inc1.quotes)
        self.assertFalse(inc2.quotes)
        self.assertTrue(inc3.quotes)

    def test_order(self):
        self.assertLess(Include.STD_C, Include.STD_CPP)
        self.assertLess(Include.CONTRIB_C, Include.CONTRIB_CPP)
        self.assertLess(Include.OWN_IFACE, Include.OWN_IMPL)


class TestIncludeNaming(unittest.TestCase):
    def setUp(self):
        self.include = Include("foobar")

    def test_quotes(self):
        self.include.quotes = True
        self.assertEqual(_l(to_string(self.include.write)), "#include \"foobar\"\n")

    def test_brackets(self):
        self.include.quotes = False
        self.assertEqual(_l(to_string(self.include.write)), "#include <foobar>\n")



if __name__ == "__main__":
    sys.exit(unittest.main())
