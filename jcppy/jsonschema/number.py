#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.numeric import Numeric

class Number(Numeric):
    def __init__(self, **kwargs):
        super(Number, self).__init__(env.number_type, kwargs.get('name'), False)
