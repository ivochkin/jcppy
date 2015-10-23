#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.cpp.namespace import Namespace, make_namespace
from tests import _l, to_string


class TestMakeNamespace(unittest.TestCase):
    def test_zero(self):
        self.assertRaises(RuntimeError, make_namespace)

    def test_one(self):
        n = make_namespace("foo")
        self.assertIsNone(n.parent)
        self.assertEqual("foo", n.name)
        self.assertEqual(1, n.nesting_level())

    def test_two(self):
        n = make_namespace("foo", "bar")
        self.assertIsNotNone(n.parent)
        self.assertIsNone(n.parent.parent)
        self.assertEqual("bar", n.name)
        self.assertEqual("foo", n.parent.name)
        self.assertEqual(2, n.nesting_level())
        self.assertEqual(1, n.parent.nesting_level())

    def test_deep_nest(self):
        ns = [str(i) for i in xrange(10)]
        n = make_namespace(*ns)
        self.assertEqual(10, n.nesting_level())
        self.assertEqual("0::1::2::3::4::5::6::7::8::9", n.full_name)


class TestNamespace(unittest.TestCase):
    def setUp(self):
        self.ns = make_namespace("foo", "bar")
        self.ns.config.indent.symbol = "  "
        self.ns.config.indent.namespace_declaration = 0
        self.ns.config.newline_before_curly_bracket = False
        self.ns.config.namespaces.group_right_brackets = True
        self.ns.config.naming.namespace = "c"
        self.ns.config.naming.namespace_prefix = ""
        self.ns.config.naming.namespace_suffix = ""

    def test_write_default(self):
        header = to_string(self.ns, self.ns.write_header)
        footer = to_string(self.ns, self.ns.write_footer)
        self.assertEqual(_l(header), "namespace foo {\nnamespace bar {\n")
        self.assertEqual(_l(footer), "}} // namespace foo::bar\n")

    def test_write_newline(self):
        self.ns.config.newline_before_curly_bracket = True
        header = to_string(self.ns, self.ns.write_header)
        footer = to_string(self.ns, self.ns.write_footer)
        self.assertEqual(_l(header), "namespace foo\n{\nnamespace bar\n{\n")
        self.assertEqual(_l(footer), "}} // namespace foo::bar\n")

    def test_csharp_style(self):
        self.ns.config.newline_before_curly_bracket = True
        self.ns.config.indent.namespace_declaration = 1
        self.ns.config.namespaces.group_right_brackets = False
        self.ns.config.indent.symbol = "\t"
        header = to_string(self.ns, self.ns.write_header)
        footer = to_string(self.ns, self.ns.write_footer)
        self.assertEqual(_l(header), "namespace foo\n{\n\tnamespace bar\n\t{\n")
        self.assertEqual(_l(footer), "} // namespace bar\n} // namespace foo\n")


class TestNaming(unittest.TestCase):
    def setUp(self):
        self.ns = make_namespace("foo.bar")

    def test_default(self):
        self.ns.config.naming.namespace = "c"
        self.ns.config.naming.namespace_prefix = ""
        self.ns.config.naming.namespace_suffix = ""
        self.assertEqual(_l(self.ns.name), "foo_bar")

    def test_tricky(self):
        self.ns.config.naming.namespace = "pascal"
        self.ns.config.naming.namespace_prefix = "N"
        self.ns.config.naming.namespace_suffix = "_"
        self.assertEqual(_l(self.ns.name), "NFooBar_")


if __name__ == "__main__":
    sys.exit(unittest.main())
