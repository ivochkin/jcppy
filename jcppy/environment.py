#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

class Environment(object):
    def __init__(self):
        self.integer_type = 'int'
        self.number_type = 'double'
        self.boolean_type = 'unsigned char'
        self.size_type = 'size_t'
        self.string_length_threshold = 32

env = Environment()
