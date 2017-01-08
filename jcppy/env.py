#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from jcppy.types import *

def make_types(typ):
    return {
        "type": typ,
        "storage_type": storage_type(typ),
        "argument_type": argument_type(typ),
        "return_type": return_type(typ),
    }

def make_names(name, property_name="name"):
    return {
        property_name: name,
        property_name.title(): name.title(),
        property_name.upper(): name.upper(),
    }
