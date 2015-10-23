#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
from StringIO import StringIO
from jcppy.writer import StreamWriter
from jcppy.cpp.config import config


def _l(s): return s.replace("\n", os.linesep)

def to_string(write_func):
    stream = StringIO()
    accumulator = StreamWriter(stream, config.indent.symbol)
    write_func(accumulator)
    return stream.getvalue()
