#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.ast
import jcppy.cpp.naming

class Namespace(cpp.ast.AST):
    def __init__(self, name, parent=None):
        super(Namespace, self).__init__(name, cpp.naming.NamespaceNaming(self))
        self.parent = parent
        if not self.parent is None:
            assert(isinstance(self.parent, Namespace))

    @property
    def refs(self):
        return [self.parent]

    @property
    def full_name(self):
        if self.parent is None:
            return self.name
        return self.parent.full_name + "::" + self.name

    def nesting_level(self):
        if self.parent is None:
            return 1
        return self.parent.nesting_level() + 1

    def write_header(self, out):
        if not self.parent is None:
            self.parent.write_header(out)
        if self.config.indent.namespace_declaration > 0:
            out = out.indent(self.config.indent.namespace_declaration * (self.nesting_level() - 1))[0]
        if self.config.newline_before_curly_bracket:
            out("namespace {0}".format(self.name))
            out("{")
        else:
            out("namespace {0} {{".format(self.name))

    def write_footer(self, out):
        if self.config.namespaces.group_right_brackets:
            out("}" * self.nesting_level() + " // namespace " + self.full_name)
        else:
            out("} // namespace " + self.name)
            if not self.parent is None:
                out = self.parent.write_footer(out)
        return out


class NamespaceFactory(object):
    def __init__(self):
        self._cache = {}

    def make(self, *names):
        if len(names) == 0:
            raise RuntimeError("at least one name is expected")
        ns_prefix = names[0]
        result = self._cache.setdefault(ns_prefix, Namespace(names[0]))
        for i in names[1:]:
            ns_prefix += "::" + i
            result = self._cache.setdefault(ns_prefix, Namespace(i, result))
        return result


def make_namespace(*names):
    return NamespaceFactory().make(*names)
