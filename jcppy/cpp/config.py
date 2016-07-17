#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

class Naming(object):
    def __init__(self):
        """Naming can be
            "camel" : camelCase
            "pascal" : PascalCase
            "c": c_case
            "upper": UPPER_CASE
        """
        self.variable = "camel"
        self.variable_prefix = ""
        self.variable_suffix = ""
        self.class_ = "pascal"
        self.class_prefix = ""
        self.class_suffix = ""
        self.method = "camel"
        self.method_prefix = ""
        self.method_suffix = ""
        self.function = "camel"
        self.function_suffix = ""
        self.function_prefix = ""
        self.member = "camel"
        self.member_suffix = "_"
        self.member_prefix = ""
        self.namespace = "c"
        self.namespace_suffix = ""
        self.namespace_prefix = ""
        self.constant = "upper"
        self.constant_prefix = ""
        self.constant_suffix = ""


class Indent(object):
    def __init__(self):
        self.symbol = "  "
        self.function_definition = 2
        self.function_declaration = 1
        self.namespace_declaration = 0
        self.class_visibility_specifier = 0


class Namespaces(object):
    def __init__(self):
        self.group_right_brackets = True


class Classes(object):
    def __init__(self):
        self.hide_private_inheritance = True


class Config(object):
    def __init__(self):
        self.naming = Naming()
        self.indent = Indent()
        self.namespaces = Namespaces()
        self.classes = Classes()
        self.newline_before_curly_bracket = False
        self.linewidth = 60
