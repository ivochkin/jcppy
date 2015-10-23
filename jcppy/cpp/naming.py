#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.cpp.config import config

class Naming(object):
    def __init__(self, style_getter, prefix_getter, suffix_getter):
        self._style = style_getter
        self._prefix = prefix_getter
        self._suffix = suffix_getter

    def __call__(self, name):
        # adjust case
        if self._style() == "pascal" or self._style() == "camel":
            parts = name.split(".")
            parts = [i[0].upper() + i[1:] for i in parts]
            if self._style() == "camel":
                parts[0] = parts[0][0].lower() + parts[0][1:]
            name = "".join(parts)
        elif self._style() == "upper":
            name = name.upper()
        elif self._style() == "c":
            name = name.lower()
        #adjust separators
        if self._style() == "c" or self._style() == "upper":
            name = name.replace(".", "_")
        # add prefix/suffix
        return self._prefix() + name + self._suffix()


function_naming = Naming(lambda: config.naming.function,
                         lambda: config.naming.function_prefix,
                         lambda: config.naming.function_suffix)

class_naming = Naming(lambda: config.naming.class_,
                      lambda: config.naming.class_prefix,
                      lambda: config.naming.class_suffix)

namespace_naming = Naming(lambda: config.naming.namespace,
                          lambda: config.naming.namespace_prefix,
                          lambda: config.naming.namespace_suffix)

variable_naming = Naming(lambda: config.naming.variable,
                         lambda: config.naming.variable_prefix,
                         lambda: config.naming.variable_suffix)

member_naming = Naming(lambda: config.naming.member,
                       lambda: config.naming.member_prefix,
                       lambda: config.naming.member_suffix)

constant_naming = Naming(lambda: config.naming.constant,
                         lambda: config.naming.constant_prefix,
                         lambda: config.naming.constant_suffix)
