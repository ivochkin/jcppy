#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

from jcppy.boolean import Boolean
from jcppy.number import Number
from jcppy.integer import Integer
from jcppy.string import String
from jcppy.array import Array
from jcppy.choice import Choice
from jcppy.json_object import JsonObject

class Any(Choice):
    def __init__(self, **kwargs):
        options = [
            Boolean(name='boolean'),
            Number(name='number'),
            Integer(name='integer'),
            String(name='string'),
            Array(JsonObject('void', None), name='array'),
        ]
        super(Any, self).__init__(*options, **kwargs)
