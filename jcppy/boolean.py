#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

from jcppy.environment import env
from jcppy.json_object import JsonObject

class Boolean(JsonObject):
    def __init__(self, **kwargs):
        super(Boolean, self).__init__(env.boolean_type, kwargs.get('name'))
