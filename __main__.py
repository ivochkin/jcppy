#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).
#
# For JSON-Schema spec, see
# http://tools.ietf.org/html/draft-fge-json-schema-validation-00
'''
Jcppy - C/C++ generator for JSON Schema written in python.
'''

__version__ = '0.1.0'

import sys
import json

from jcppy.json_object import JsonObject
from jcppy.number import Number
from jcppy.integer import Integer
from jcppy.string import String
from jcppy.one_of import OneOf
from jcppy.choice import Choice
from jcppy.array import Array
from jcppy.tuple import Tuple
from jcppy.any import Any
from jcppy.writer import StreamWriter

def number():
    a = Number()
    a.maximum = 10.0
    a.ex_maximum = True
    a.minimum = -0.5
    return a

def integer():
    a = Integer()
    a.maximum = 100
    a.minimum = 1
    a.ex_minimum = True
    return a

def string():
    a = String()
    a.min_length = 1
    a.max_length = 100
    return a

def string2():
    a = String()
    a.min_length = a.max_length = 20
    return a

def choice():
    a = string()
    b = string2()
    c = number()
    b.name = 'surname'
    c.name = 'age'
    d = Choice(a,b,c)
    return d

def array():
    return Array(choice())

def array2():
    a = Array(JsonObject('void', None))
    a.min_items = 10
    a.max_items = 15
    return a

def tuple_():
    b = Tuple(choice(), string(), number())
    return b

def tuple2():
    a = Integer()
    a.minimum = 1
    a.maximum = 3
    a.name = 'integer'
    b = String()
    b.name = 'name'
    c = Tuple(a, b)
    d = Tuple(a, c)
    e = Tuple(d, b)
    return e

def any_():
    return Any()

def main():
    o = StreamWriter(sys.stdout)
    cases = [
        number,
        integer,
        string,
        string2,
        choice,
#        array,
#        array2,
#        tuple_,
#        tuple2,
#        any_,
    ]
    for i in cases:
        print '-' * 10 + str(i) + '-' * 10
        a = i()
        a.typedef(o, 'type')
        a.variable(o, 'foo')
        a.validate(o, 'foo')
        a.operator_equal(o, 'foo', 'bar')
        a.operator_less(o, 'foo', 'bar')
        o.flush()

if __name__ == '__main__':
    sys.exit(main())
