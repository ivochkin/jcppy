#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.cpp.config import config
from jcppy.cpp.ast import AST
from jcppy.cpp.naming import namespace_naming

class Namespace(AST):
    def __init__(self, name, parent=None):
        super(Namespace, self).__init__(name, namespace_naming)
        self.parent = parent
        if not self.parent is None:
            assert(isinstance(self.parent, Namespace))

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
        if config.indent.namespace_declaration > 0:
            out = out.indent(config.indent.namespace_declaration * (self.nesting_level() - 1))[0]
        if config.newline_before_curly_bracket:
            out("namespace {}".format(self.name))
            out("{")
        else:
            out("namespace {} {{".format(self.name))

    def write_footer(self, out):
        if config.namespaces.group_right_brackets:
            out("}" * self.nesting_level() + " // namespace " + self.full_name)
        else:
            out("} // namespace " + self.name)
            if not self.parent is None:
                out = self.parent.write_footer(out)
        return out


def make_namespace(*names):
    if len(names) == 0:
        raise RuntimeError("at least one name is expected")
    result = Namespace(names[0])
    for i in names[1:]:
        result = Namespace(i, result)
    return result
