#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

try:
    from jcppy._version import __version__, __revision__
except ImportError:
    __version__ = 'latest'
    __revision__ = 'latest'
    __hash__ = 'unknown'
from jcppy.header import header
from jcppy.source import source
