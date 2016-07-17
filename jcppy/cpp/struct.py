#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.naming
import jcppy.cpp.ast


class _Visibility(object):
    def __init__(self, name):
        self.name = name
        self.methods = []
        self.members = []
        self.consts = []
        self.functions = []
        self.base = []

    def has_any(self):
        return len(self.methods) > 0 or\
               len(self.members) > 0 or\
               len(self.consts) > 0 or\
               len(self.functions) > 0


class Class(cpp.ast.AST):
    def __init__(self, name, namespace=None):
        super(Class, self).__init__(name, cpp.naming.ClassNaming(self))
        self.struct = False
        self.namespace = namespace
        self.includes = []
        self.public = _Visibility("public")
        self.protected = _Visibility("protected")
        self.private = _Visibility("private")
        self._all_vis = [self.public, self.protected, self.private]
        self.destructor = None

    @property
    def refs(self):
        allrefs = [self.namespace] + self.includes
        for vis in self._all_vis:
            allrefs += vis.methods
            allrefs += vis.members
            allrefs += vis.consts
            allrefs += vis.functions
        return allrefs

    def write_declaration(self, out):
        struct = "struct" if self.struct else "class"

        decl_length = len(struct) + 1 + len(self.name)
        bases = []
        for vis in self._all_vis:
            for base in vis.base:
                decl_length += len(vis.name) + len(base) + 1
                if self.config.classes.hide_private_inheritance and vis.name == "private":
                    bases.append("{0}".format(base))
                else:
                    bases.append("{0} {1}".format(vis.name, base))
        if decl_length > self.config.linewidth and len(bases):
            out("{0} {1}".format(struct, self.name))
            iout = out.indent()[0]
            iout(": {0}".format(bases[0]))
            for i in bases[1:-1]:
                iout(", " + i)
            if self.config.newline_before_curly_bracket:
                iout(", " + bases[-1])
                out("{")
            else:
                iout("{0} {{".format(bases[-1]))
        else:
            inheritance = " : " + ", ".join(bases) if len(bases) else ""
            if self.config.newline_before_curly_bracket:
                out("{0} {1}{2}".format(struct, self.name, inheritance))
                out("{")
            else:
                out("{0} {1}{2} {{".format(struct, self.name, inheritance))

        def _write_visibility(vis, out):
            if not vis.has_any():
                return

            if self.config.indent.class_visibility_specifier > 0:
                out = out.indent(self.config.indent.class_visibility_specifier)[0]

            out("{0}:".format(vis.name))

            out = out.indent()[0]

            for const in vis.consts:
                const.write(out)

            if len(vis.consts) and len(vis.functions):
                out()

            for func in vis.functions:
                func.write_declaration(out)

            if len(vis.functions) and len(vis.methods):
                out()

            for meth in vis.methods:
                meth.write_declaration(out)

            if len(vis.methods) and len(vis.members):
                out()

            for member in vis.members:
                member.write(out)

        for vis in [self.public, self.protected]:
            _write_visibility(vis, out)
            if vis.has_any():
                out()
        _write_visibility(self.private, out)

        out("};")


class Struct(Class):
    def __init__(self, *args, **kwargs):
        super(Struct, self).__init__(*args, **kwargs)
        self.struct = True
