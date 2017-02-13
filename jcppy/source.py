#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import pkg_resources
from jcppy.render import render
from jcppy.env import make_names, make_types

def make_property_env(schema, prop_name, prop):
    required = prop_name in schema.get("required", [])
    e = {
        "required": required,
        "optional": not required,
        "class_name": schema["title"],
    }
    e.update(make_names(prop_name))
    e.update(make_names(schema["title"], property_name="class_name"))
    e.update(make_types(prop["type"]))
    return e


def source(env, schema):
    embedjson = open(pkg_resources.resource_filename("jcppy", "data/embedjson.c")).read()
    yield render("source_header.cpp", env,
            {"embedjson": embedjson}, make_names(schema["title"]))
    for prop_name, prop in schema["properties"].items():
        if prop["type"] in ["object", "array"]:
            continue
        e = make_property_env(schema, prop_name, prop)
        yield render("primitive_property.cpp", env, e)
    all_properties = []
    found_first_required = False
    found_leading_optional = False
    for prop_name, prop in schema["properties"].items():
        if prop["type"] in ["object", "array"]:
            continue
        penv = make_property_env(schema, prop_name, prop)
        if found_first_required:
            penv["can_be_first_in_json"] = False
            penv["first_in_json"] = False
        else:
            penv["can_be_first_in_json"] = True
            penv["first_in_json"] = penv["required"] and not found_leading_optional
            if penv["optional"]:
                found_leading_optional = True
            else:
                found_first_required = True
        all_properties.append(penv)
    rw_env = {
        "properties": all_properties
    }
    yield render("reader.cpp", env, make_names(schema["title"]), rw_env)
    yield render("writer.cpp", env, make_names(schema["title"]), rw_env)
