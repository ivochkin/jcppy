#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.struct


class Type(object):
    def __init__(self, typ):
        self._type = typ
        self._pointer = False
        self._reference = False
        self._const = False

    @property
    def typ(self):
        return self._type

    @typ.setter
    def typ(self, typ):
        if not isinstance(typ, (str, cpp.struct.Class, cpp.struct.Struct)):
            raise RuntimeError("Type can either str, or jcppy.cpp.struct.Class")
        if isinstance(typ, str):

            class UnknownType(object):
                def __init__(self, typ):
                    self._type = typ

                @property
                def name(self):
                    return self._type

            self._type = UnknownType(typ)
        else:
            self._type = typ

    @property
    def pointer(self):
        return self._pointer

    @pointer.setter
    def pointer(self, pointer):
        self._pointer = pointer

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, reference):
        self._reference = reference

    @property
    def const(self):
        return self._const

    @const.setter
    def const(self, const):
        self._const = const

    def format_self(self):
        ref = ""
        if self.pointer:
            ref = "*"
        elif self.reference:
            ref = "&"
        const = "const " if self.const else ""
        typ = self.typ
        if not self.is_bultin_type():
            typ = self.typ.name
        return "".join([const, typ, ref])

    def format_var(self, var):
        return "{0} {1}".format(self.format_self(), var.name)

    def is_bultin_type(self):
        return not isinstance(self.typ, (cpp.struct.Class, cpp.struct.Struct))
