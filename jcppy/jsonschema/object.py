#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.environment import env
from jcppy.json_object import JsonObject

class Object(JsonObject):
    def __init__(self, *members):
        super(Object, self).__init__(None)
        self.members = members
