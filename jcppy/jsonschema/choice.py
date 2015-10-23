#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.json_object import JsonObject

def _getname(opt, default):
    return opt.name if opt.name else default

class Choice(JsonObject):
    def __init__(self, *options, **kwargs):
        super(Choice, self).__init__(None, kwargs.get('name'))
        self.options = options

    def _struct_internals(self, o):
        for i, opt in enumerate(self.options):
            o('unsigned char is_{}:1;'.format(_getname(opt, str(i))))
        if len(self.options) == 0:
            return
        o('union {')
        for i, opt in enumerate(self.options):
            opt.variable(o.indent(), _getname(opt, str(i)))
        o('}')

    def typedef(self, o, typename):
        o('typedef struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(typename))

    def variable(self, o, name):
        o('struct {')
        self._struct_internals(o.indent())
        o('}} {};'.format(name))

    def validate(self, o, varname):
        if len(self.options):
            terms = []
            for i, opt in enumerate(self.options):
                terms.append('{}.is_{}'.format(varname, _getname(opt, str(i))))
            exp = ' + '.join(terms)
            o('// Ensure that exactly one option is chosen')
            o('if (({}) != 1) {{'.format(exp))
            o('return -1;', indent=1)
            o('}')

        for i, opt in enumerate(self.options):
            name = _getname(opt, str(i))
            o('')
            if not opt.validate(o.fake(), None):
                o('// Field {} has no validation'.format(name))
                continue
            o('// Validation of the field "{}"'.format(name))
            o('if ({}.is_{}) {{'.format(varname, name))
            opt.validate(o.indent(), '{}.{}'.format(varname, name))
            o('}')

        return len(self.options) > 0
