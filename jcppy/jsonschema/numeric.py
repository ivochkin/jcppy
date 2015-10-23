#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.json_object import JsonObject

class Numeric(JsonObject):
    def __init__(self, storage_type, name, has_strict_cmp):
        super(Numeric, self).__init__(storage_type, name)
        self._has_strict_cmp = has_strict_cmp
        self.multiple_of = None
        self.maximum = None
        self.ex_maximum = None
        self.minimum = None
        self.ex_minimum = None

    def validate(self, o, varname):
        need_validate = False
        if not self.maximum is None:
            need_validate = True
            sign = '<' if self.ex_maximum else '<='
            o('if ({} {} {}) {{'.format(varname, sign, self.maximum))
            o('return -1;', indent=1)
            o('}')

        if not self.minimum is None:
            need_validate = True
            sign = '>' if self.ex_minimum else '>='
            o('if ({} {} {}) {{'.format(varname, sign, self.minimum))
            o('return -1;', indent=1)
            o('}')

        if not self.multiple_of is None:
            need_validate = True
            comp = '!= 0' if self._has_strict_cmp else '< JCPPY_EPSILON'
            o('if (({} % {}) {}) {{'.format(varname, self.multiple_of, comp))
            o('return -1;', indent=1)
            o('}')

        return need_validate
