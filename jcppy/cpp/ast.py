#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

class AST(object):
    def __init__(self, name=None, naming=lambda x: x):
        self._name = name
        self._naming = naming

    @property
    def name(self):
        if self._naming is None:
            return self._name
        return self._naming(self._name)

    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return "<AST {}>".format(self._name)
