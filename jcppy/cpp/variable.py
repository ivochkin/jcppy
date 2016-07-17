#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.naming
import jcppy.cpp.ast

class Variable(cpp.ast.AST):
    def __init__(self, typ, name):
        super(Variable, self).__init__(name, cpp.naming.VariableNaming(self))
        self._type = typ

    @property
    def typ(self):
        return self._type

    @typ.setter
    def typ(self, typ):
        self._type = typ

    def write(self, out):
        out(self._type.format_var(self) + ";")

    def format_self(self):
        return self._type.format_var(self)
