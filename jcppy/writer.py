#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

import os
from copy import copy

class FakeWriter(object):
    def __call__(*_, **__):
        pass
    def fake(self):
        return self
    def indent(self, *_):
        return self
    def include(self, *_):
        pass

class StreamWriter(object):
    def __init__(self, out, indent_str='  ', indent_level=0):
        self.out = out
        self.indent_str = indent_str
        self.indent_level = indent_level
        self.headers = set()
        self.lines = []

    def __call__(self, line, indent=0):
        indentation = self.indent_str * (self.indent_level + indent)
        self.lines.append(indentation + str(line))

    def indent(self, count=1):
        if count < 1:
            raise ValueError('count')
        a = copy(self)
        a.indent_level += count
        if count == 1:
            return a
        elif count == 2:
            return (self.indent(), a)
        else:
            return tuple(list(self.indent(count - 1)) + [a])

    def fake(self):
        return FakeWriter()

    def include(self, header):
        self.headers.add(header)

    def flush(self):
        if len(self.headers):
            inclines = ['#include <{}>'.format(i) for i in self.headers]
            self.out.write(os.linesep.join(inclines))
            self.out.write(os.linesep)
        self.out.write(os.linesep.join(self.lines))
        self.out.write(os.linesep)
        self.lines = []
        self.headers = set()
