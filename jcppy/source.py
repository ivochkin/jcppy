#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import pkg_resources
from jcppy.render import render
from jcppy.env import make_names, make_types

def source(env, schema):
    embedjson = open(pkg_resources.resource_filename("jcppy", "data/embedjson.c")).read()
    yield render("source_header.cpp", env,
            {"embedjson": embedjson}, make_names(schema["title"]))
    for prop_name, prop in schema["properties"].items():
        if prop["type"] not in ["object", "array"]:
            required = prop_name in schema.get("required")
            e = {
                "required": required,
                "optional": not required,
                "class_name": schema["title"],
            }
            e.update(make_names(prop_name))
            e.update(make_names(schema["title"], property_name="class_name"))
            e.update(make_types(prop["type"]))
            yield render("primitive_property.cpp", env, e)
    yield render("reader.cpp", env, make_names(schema["title"]))
    yield render("writer.cpp", env, make_names(schema["title"]))
