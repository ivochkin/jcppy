#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.json_object import JsonObject

def getname(opt, default):
    return opt.name if opt.name else default

class Tuple(JsonObject):
    def __init__(self, additional_items, *options, **kwargs):
        super(Tuple, self).__init__(None, kwargs.get('name'))
        self.options = options
        self.additional_items = additional_items

    def _struct_internals(self, o):
        for i, opt in enumerate(self.options):
            opt.variable(o.indent(), getname(opt, str(i)))

    def typedef(self, o, typename):
        o('typedef struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(typename))

    def variable(self, o, name):
        o('struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(name))

    def validate(self, o, varname):
        for i, opt in enumerate(self.options):
            name = getname(opt, str(i))
            if i > 1:
                o('')
            if not opt.validate(o.fake(), None):
                o('// Field {} has no validation'.format(name))
            else:
                o('// Validation of the field "{}"'.format(name))
                opt.validate(o, '{}.{}'.format(varname, name))
        return len(self.options) > 0
