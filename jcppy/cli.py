#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
import sys
import json
import click
import jcppy

@click.command()
@click.argument("schema", type=click.File("r"))
@click.option("--header", type=click.File("w"), default="jcppy_generated.h")
@click.option("--source", type=click.File("w"), default="jcppy_generated.cpp")
@click.version_option("~".join([jcppy.__version__, jcppy.__revision__]))
def cli(schema, header, source):
    s = json.load(schema)
    env = {
        "jcppy_version": jcppy.__version__,
        "jcppy_revision": jcppy.__revision__,
        "schema_filename": os.path.basename(schema.name),
        "header_filename": os.path.basename(header.name),
        "source_filename": os.path.basename(source.name),
    }
    for i in jcppy.header(env, s):
        header.write(i)
    for i in jcppy.source(env, s):
        source.write(i)
    return 0

def main():
    cli()

if __name__ == "__main__":
    sys.exit(main())
