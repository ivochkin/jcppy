#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
from jinja2 import Environment, PackageLoader, FileSystemLoader
from jcppy import __version__, __revision__


def render(template, *envs):
    environment = Environment(loader=PackageLoader("jcppy", os.path.join("data", "templates")))
    environment.trim_blocks = True
    environment.lstrip_blocks = True
    env = {}
    for e in envs:
        env.update(e)
    return environment.get_template(template).render(env)
