#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.json_object import JsonObject

class Array(JsonObject):
    def __init__(self, element, **kwargs):
        super(Array, self).__init__(None, kwargs.get('name'))
        self.min_items = None
        self.max_items = None
        self.unique_items = None
        self.element = element

    def _struct_internals(self, o):
        self.element.variable(o, '*data')
        o('{0} size;'.format(env.size_type))

    def typedef(self, o, typename):
        o('typedef struct {')
        self._struct_internals(o.indent())
        o('}} {0};'.format(typename))

    def variable(self, o, name):
        o('struct {')
        self._struct_internals(o.indent())
        o('}} {0};'.format(name))

    def validate(self, o, varname):
        need_validate = False
        cases = [(self.min_items, '<'), (self.max_items, '>')]
        for prop, sign in cases:
            if not prop is None:
                need_validate = True
                o('if ({0}.size {1} {2}) {{'.format(varname, sign, prop))
                o('return -1;', indent=1)
                o('}')
        return need_validate
