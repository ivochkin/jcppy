#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

class Naming(object):
    def __init__(self, style_getter, prefix_getter, suffix_getter):
        self._style = style_getter
        self._prefix = prefix_getter
        self._suffix = suffix_getter

    def __call__(self, name):
        # adjust case
        if self._style() == "pascal" or self._style() == "camel":
            parts = name.split(".")
            parts = [i[0].upper() + i[1:] for i in parts]
            if self._style() == "camel":
                parts[0] = parts[0][0].lower() + parts[0][1:]
            name = "".join(parts)
        elif self._style() == "upper":
            name = name.upper()
        elif self._style() == "c":
            name = name.lower()
        #adjust separators
        if self._style() == "c" or self._style() == "upper":
            name = name.replace(".", "_")
        # add prefix/suffix
        return self._prefix() + name + self._suffix()


class FunctionNaming(Naming):
    def __init__(self, ast):
        super(FunctionNaming, self).__init__(lambda: ast.config.naming.function,
                                            lambda: ast.config.naming.function_prefix,
                                            lambda: ast.config.naming.function_suffix)


class ClassNaming(Naming):
    def __init__(self, ast):
        super(ClassNaming, self).__init__(lambda: ast.config.naming.class_,
                                            lambda: ast.config.naming.class_prefix,
                                            lambda: ast.config.naming.class_suffix)


class NamespaceNaming(Naming):
    def __init__(self, ast):
        super(NamespaceNaming, self).__init__(lambda: ast.config.naming.namespace,
                                            lambda: ast.config.naming.namespace_prefix,
                                            lambda: ast.config.naming.namespace_suffix)


class VariableNaming(Naming):
    def __init__(self, ast):
        super(VariableNaming, self).__init__(lambda: ast.config.naming.variable,
                                            lambda: ast.config.naming.variable_prefix,
                                            lambda: ast.config.naming.variable_suffix)


class MemberNaming(Naming):
    def __init__(self, ast):
        super(MemberNaming, self).__init__(lambda: ast.config.naming.member,
                                            lambda: ast.config.naming.member_prefix,
                                            lambda: ast.config.naming.member_suffix)


class ConstantNaming(Naming):
    def __init__(self, ast):
        super(ConstantNaming, self).__init__(lambda: ast.config.naming.constant,
                                            lambda: ast.config.naming.constant_prefix,
                                            lambda: ast.config.naming.constant_suffix)
