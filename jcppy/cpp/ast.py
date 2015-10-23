#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

from __future__ import print_function
import jcppy.cpp.config

class AST(object):
    def __init__(self, name=None, naming=lambda x: x, parent=None):
        self._name = name
        self._naming = naming
        self._parent = parent
        if self._parent is None:
            self._config = jcppy.cpp.config.Config()
        else:
            self._config = None
        self._chld = []

    @property
    def name(self):
        if self._naming is None:
            return self._name
        return self._naming(self._name)

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def config(self):
        if self._parent is None:
            return self._config
        else:
            return self._parent.config

    @config.setter
    def config(self, new):
        if self._parent is None:
            self._config = new
        else:
            self._parent.config = new

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new):
        if not self._parent is None:
            self._parent._chld.remove(self)
        if self._parent is None and not new is None:
            self._config = None
        self._parent = new
        if not self._parent is None:
            self._parent._chld.append(self)

    def print_tree(self, indent=0):
        print("  " * indent + str(self))
        for chld in self._chld:
            chld.print_tree(indent + 1)

    def __str__(self):
        return "<AST {0}>".format(self._name)
