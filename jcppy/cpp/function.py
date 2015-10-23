#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.ast
import jcppy.cpp.naming
import jcppy.cpp.include
import jcppy.cpp.struct
import jcppy.cpp.namespace
import jcppy.cpp.type_

class Function(cpp.ast.AST):
    def __init__(self, name):
        super(Function, self).__init__(name, cpp.naming.FunctionNaming(self))
        self._namespace = None
        self._returns = cpp.type_.Type("void")
        self._args = []
        self._includes = []
        self._static = False
        self._virtual = False
        self._pure_virtual = False
        self._cls = None

    # RW properties

    @property
    def namespace(self):
        return self._namespace
    @namespace.setter
    def namespace(self, new):
        if not isinstance(new, cpp.namespace.Namespace):
            raise RuntimeError("bad namespace type")
        if not self._cls is None and not new is None:
            raise RuntimeError("method can not have namespace")
        self._namespace = new

    @property
    def returns(self):
        return self._returns
    @returns.setter
    def returns(self, new):
        if new is None:
            new = cpp.type_.Type("void")
        if not isinstance(new, cpp.type_.Type):
            raise RuntimeError("bad return type")
        self._returns = new

    @property
    def args(self):
        return self._args
    @args.setter
    def args(self, new):
        self._args = new

    @property
    def includes(self):
        return self._includes
    @includes.setter
    def includes(self, new):
        self._includes = new

    @property
    def static(self):
        return self._static
    @static.setter
    def static(self, new):
        if self.virtual:
            raise RuntimeError("virtual function can not be static")
        self._static = bool(new)

    @property
    def virtual(self):
        return self._virtual
    @virtual.setter
    def virtual(self, new):
        if new and self._cls is None:
            raise RuntimeError("non-method can not be virtual")
        if self.static:
            raise RuntimeError("static functions can not be virtual")
        self._virtual = bool(new)

    @property
    def pure_virtual(self):
        return self._pure_virtual
    @pure_virtual.setter
    def pure_virtual(self, new):
        self.virtual = True
        self._pure_virtual = bool(new)

    @property
    def cls(self):
        return self._cls
    @cls.setter
    def cls(self, new):
        if not isinstance(new, cpp.struct.Class):
            raise RuntimeError("can not attach method to non-Class")
        if not self._namespace is None:
            raise RuntimeError("function within namespace can not become a method")
        self._cls = new

    # computed properties
    @property
    def specifier(self):
        ret = ""
        if self.static:
            ret = "static"
        elif self.virtual:
            ret = "virtual"
        return ret

    @property
    def declaration(self):
        return "{}{}{} {}({}){};".format(self.specifier,
                                         " " if len(self.specifier) else "",
                                         self.returns.format_self(),
                                         self.name,
                                         ", ".join([i.format_self() for i in self.args]),
                                         " = 0" if self.pure_virtual else "")

    def write_declaration(self, out):
        if len(self.declaration) <= self.config.linewidth or len(self.args) == 0:
            out(self.declaration)
            return

        out("{}{}{} {}(".format(self.specifier,
                                " " if len(self.specifier) else "",
                                self.returns.format_self(),
                                self.name))
        indent = out.indent(self.config.indent.function_declaration)[-1]
        for arg in self.args[:-1]:
            indent(arg.format_self() + ",")
        indent("{}){};".format(self.args[-1].format_self(), " = 0" if self.pure_virtual else ""))

    def __str__(self):
        return "<Function {}>".format(self.declaration)
