#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
import json
import jcppy
import subprocess


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class JcppyEmulator(object):
    def __init__(self, working_dir):
        self._directory = working_dir

    def directory(self):
        return self._directory

    def generate(self, schema):
        parsed_schema = json.loads(schema)
        source_filename = os.path.join(self.directory(), "generated.cpp")
        header_filename = os.path.join(self.directory(), "generated.h")
        schema_filename = os.path.join(self.directory(), "generated.json")
        env = {
            "jcppy_version": jcppy.__version__,
            "jcppy_revision": jcppy.__revision__,
            "schema_filename": schema_filename,
            "header_filename": header_filename,
            "source_filename": source_filename,
        }
        with open(header_filename, 'w') as f:
            for header_chunk in jcppy.header(env, parsed_schema):
                f.write(header_chunk)
        with open(source_filename, 'w') as f:
            for source_chunk in jcppy.source(env, parsed_schema):
                f.write(source_chunk)
        return (
            [source_filename],
            [header_filename],
        )

    def compile_and_run(self, *sources):
        with cd(self._directory):
            args = ["g++"]
            for src in sources:
                args.append(src)
            subprocess.check_call(args)
            output = subprocess.check_output(["./a.out"])
            return output.decode().strip()
