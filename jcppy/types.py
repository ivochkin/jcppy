#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

def storage_type(typ):
    return {
        "integer": "int64_t",
        "number": "double",
        "string": "std::string",
        "boolean": "bool",
    }.get(typ)

def argument_type(typ):
    return {
        "integer": "int64_t",
        "number": "double",
        "string": "const std::string&",
        "boolean": "bool",
    }.get(typ)

def return_type(typ):
    return argument_type(typ)
