#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
from jcppy.cpp.config import config
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
        super(Class, self).__init__(name, cpp.naming.class_naming)
        self.struct = False
        self.namespace = namespace
        self.includes = []
        self.public = _Visibility("public")
        self.protected = _Visibility("protected")
        self.private = _Visibility("private")
        self._all_vis = [self.public, self.protected, self.private]
        self.destructor = None

    def write_declaration(self, out):
        struct = "struct" if self.struct else "class"

        decl_length = len(struct) + 1 + len(self.name)
        bases = []
        for vis in self._all_vis:
            for base in vis.base:
                decl_length += len(vis.name) + len(base) + 1
                if config.classes.hide_private_inheritance and vis.name == "private":
                    bases.append("{}".format(base))
                else:
                    bases.append("{} {}".format(vis.name, base))
        if decl_length > config.linewidth and len(bases):
            out("{} {}".format(struct, self.name))
            iout = out.indent()[0]
            iout(": {}".format(bases[0]))
            for i in bases[1:-1]:
                iout(", " + i)
            if config.newline_before_curly_bracket:
                iout(", " + bases[-1])
                out("{")
            else:
                iout("{} {{".format(bases[-1]))
        else:
            inheritance = " : " + ", ".join(bases) if len(bases) else ""
            if config.newline_before_curly_bracket:
                out("{} {}{}".format(struct, self.name, inheritance))
                out("{")
            else:
                out("{} {}{} {{".format(struct, self.name, inheritance))

        def _write_visibility(vis, out):
            if not vis.has_any():
                return

            if config.indent.class_visibility_specifier > 0:
                out = out.indent(config.indent.class_visibility_specifier)[0]

            out("{}:".format(vis.name))

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