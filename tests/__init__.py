#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from jcppy.writer import StreamWriter

def _l(s): return s.replace("\n", os.linesep)

def to_string(obj, write_func=None):
    stream = StringIO()
    accumulator = StreamWriter(stream, obj.config.indent.symbol)
    if write_func is None:
        obj.write(accumulator)
    else:
        write_func(accumulator)
    return stream.getvalue()
