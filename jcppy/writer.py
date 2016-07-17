#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

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

    def __call__(self, line=None, indent=0):
        indentation = self.indent_str * (self.indent_level + indent)
        if line is None:
            self.out.write(os.linesep)
        else:
            self.out.write(indentation + str(line) + os.linesep)

    def indent(self, count=1):
        if count < 0:
            raise ValueError('count')
        if count == 0:
            return (self,)
        a = copy(self)
        a.indent_level += count
        if count == 1:
            return (a,)
        else:
            return tuple(list(self.indent(count - 1)) + [a])

    def fake(self):
        return FakeWriter()
