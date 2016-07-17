#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.json_object import JsonObject

class String(JsonObject):
    def __init__(self, **kwargs):
        super(String, self).__init__(None, kwargs.get('name'))
        self.min_length = None
        self.max_length = None
        self.pattern = None

    def _inline_storage(self):
        if self.max_length is None:
            return False
        return self.min_length == self.max_length or self.max_length < env.string_length_threshold

    def _struct_internals(self, o):
        if self._inline_storage():
            o('char data[{}];'.format(self.max_length))
        else:
            o('char *data;')
        o('{} len;'.format(env.size_type))

    def typedef(self, o, typename):
        o('typedef struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(typename))

    def variable(self, o, name):
        o('struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(name))

    def validate(self, o, varname):
        if not self.pattern is None:
            raise Exception('not implemented')
        need_validate = False
        for prop, sign in [(self.min_length, '<'), (self.max_length, '>')]:
            if not prop is None:
                need_validate = True
                o('if ({}.len {} {}) {{'.format(varname, sign, prop))
                o('return -1;', indent=1)
                o('}')
        return need_validate

    def operator_equal(self, o, this, other):
        o.include('string.h')
        o('if ({}.len != {}.len) {{'.format(this, other))
        o('return 0;', indent=1)
        o('}')
        o('if (strncmp({0}, {1}, {0}.len) != 0) {{'.format(this, other))
        o('return 0;', indent=1)
        o('}')

    def operator_less(self, o, this, other):
        oo, ooo, oooo = o.indent(3)
        o.include('string.h')
        o('switch (strncmp({0}, {1}, JCPPY_MIN({0}.len, {1}.len))) {{'.format(this, other))
        oo('case -1: // "{}" is less than "{}"'.format(this, other))
        ooo('break;')
        oo('case 0: // first JCPPY_MIN(...) bytes of "{}" and "{}" are equal'.format(this, other))
        ooo('if ({}.len > {}.len) {{'.format(other, this))
        oooo('return 0;')
        ooo('}')
        ooo('break;')
        oo('case 1: // "{}" is greater than "{}"'.format(this, other))
        ooo('return 0;')
        o('}')

