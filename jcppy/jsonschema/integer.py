#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.numeric import Numeric

class Integer(Numeric):
    def __init__(self, **kwargs):
        super(Integer, self).__init__(env.integer_type, kwargs.get('name'), True)
