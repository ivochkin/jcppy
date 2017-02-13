#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
import unittest
import tempfile
import shutil
from .emulator import JcppyEmulator

class FunctionalTestCase(unittest.TestCase):
    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.directory = tempfile.mkdtemp()
        self.emulator = JcppyEmulator(self.directory)

    def tearDown(self):
        shutil.rmtree(self.directory)
        super(FunctionalTestCase, self).tearDown()

    def jcppy(self, schema, main_cpp, expected_stdout):
        srcs, hdrs = self.emulator.generate(schema)

        with open(os.path.join(self.directory, "main.cpp"), "w") as f:
            f.write(main_cpp)
        stdout = self.emulator.compile_and_run("main.cpp", *srcs)
        self.assertEqual(expected_stdout, stdout)
