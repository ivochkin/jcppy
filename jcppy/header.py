#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
from jcppy.render import render
from jcppy.env import make_names, make_types

def header(env, schema):
    if schema["type"] != "object":
        raise RuntimeError("Root schema should be \"object\"")
    yield render("class_header.h", env, make_names(schema["title"]))
    for prop_name, prop in schema["properties"].items():
        if prop["type"] not in ["object", "array"]:
            required = prop_name in schema.get("required", [])
            e = {
                "required": required,
                "optional": not required,
            }
            e.update(make_names(prop_name))
            e.update(make_types(prop["type"]))
            yield render("primitive_property.h", env, e)
    yield "private:" + os.linesep
    for prop_name, prop in schema["properties"].items():
        if prop["type"] not in ["object", "array"]:
            required = prop_name in schema.get("required", [])
            e = {
                "required": required,
                "optional": not required,
            }
            e.update(make_names(prop_name))
            e.update(make_types(prop["type"]))
            yield render("property_storage.h", env, e)
    envs = [env, make_names(schema["title"])]
    yield render("class_footer.h", *envs)
    yield render("reader.h", *envs)
    yield render("writer.h", *envs, {"nproperties": len(schema["properties"])})
    yield render("class_template_impl.h", *envs)
    yield render("reader_impl.h", *envs)
    yield render("writer_impl.h", *envs)
