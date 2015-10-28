#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp.config
import jcppy.builder


class AST(object):
    def __init__(self, name=None, naming=lambda x: x):
        self._name = name
        self._naming = naming
        self._config = jcppy.cpp.config.Config()

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
        return self._config

    @config.setter
    def config(self, new):
        self._config = new

    @property
    def refs(self):
        """To be overriden"""
        return []

    def apply_config(self, new):
        exclude_none = lambda x: [i for i in x if not i is None]
        allrefs = set([self])
        new_refs_found = True
        while new_refs_found:
            new_refs_found = False
            newrefs = allrefs.copy()
            for ast in allrefs:
                for ref in exclude_none(ast.refs):
                    newrefs.add(ref)
            if len(newrefs) > len(allrefs):
                new_refs_found = True
                allrefs = newrefs

        for ast in allrefs:
            ast.config = new

    def __str__(self):
        return "<AST {0}>".format(self._name)
