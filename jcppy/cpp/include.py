#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import jcppy.cpp as cpp
import jcppy.cpp.ast

class Include(cpp.ast.AST):
    STD_C = 0
    STD_CPP = 1
    CONTRIB_C = 3
    CONTRIB_CPP = 4
    OWN_IFACE = 5
    OWN_IMPL = 6

    def __init__(self, name, quotes=None, brackets=None):
        super(Include, self).__init__(name)

        assert(quotes is None or brackets is None)
        if not quotes is None:
            self._quotes = quotes
        elif not brackets is None:
            self._quotes = not brackets
        else:
            self._quotes = False

        self._order = self.STD_CPP

    @property
    def order(self):
        return self._order
    @order.setter
    def order(self, new):
        self._order = new

    @property
    def quotes(self):
        return self._quotes
    @quotes.setter
    def quotes(self, new):
        self._quotes = new

    def write(self, out):
        brackets = ("\"", "\"") if self.quotes else ("<", ">")
        out("#include {0}{1}{2}".format(brackets[0], self.name, brackets[1]))
