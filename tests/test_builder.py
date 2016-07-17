#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.builder import Builder

class Foo(object):
    def __init__(self, bar1, bar2, bar3):
        self._bar1 = bar1
        self._bar2 = bar2
        self._bar3 = bar3

    @property
    def bar1(self):
        return self._bar1
    @bar1.setter
    def bar1(self, value):
        self._bar1 = value

    @property
    def bar2(self):
        return self._bar2
    @bar2.setter
    def bar2(self, value):
        self._bar2 = value

    @property
    def bar3(self):
        return self._bar3
    @bar3.setter
    def bar3(self, value):
        self._bar3 = value


class TestBuilder(unittest.TestCase):
    def test_simple_builder(self):
        builder = Builder(Foo, True, 10, "quax")
        foo = builder.bar1(False).bar3("qq").bar2(15.4).wrap()
        self.assertEqual(False, foo.bar1)
        self.assertEqual("qq", foo.bar3)
        self.assertEqual(15.4, foo.bar2)


if __name__ == "__main__":
    sys.exit(unittest.main())
