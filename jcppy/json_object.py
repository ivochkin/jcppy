#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

class JsonObject(object):
    def __init__(self, storage_type, name=None):
        self.storage_type = storage_type
        self.name = name

    def typedef(self, o, typename):
        o('typedef {} {};'.format(self.storage_type, typename))

    def variable(self, o, name):
        o('{} {};'.format(self.storage_type, name))

    def validate(self, o, varname):
        return False

    def operator_less(self, o, this, other):
        o('if ({} >= {}) {{'.format(this, other))
        o('return 0;', indent=1)
        o('}')

    def operator_equal(self, o, this, other):
        o('if ({} != {}) {{'.format(this, other))
        o('return 0;', indent=1)
        o('}')
