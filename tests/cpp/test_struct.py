#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
import sys
from jcppy.builder import build
from jcppy.cpp.struct import Class
from jcppy.cpp.type_ import Type
from jcppy.cpp.variable import Variable
from jcppy.cpp.function import Function
from tests import _l, to_string


class TestClass(unittest.TestCase):
    def setUp(self):
        self.cls = Class("mega.manager")
        self.cls.public.base.append("std::thread")
        self.cls.private.base.append("boost::noncopyable")
        self.cls.private.members.append(Variable(Type("int"), "id"))
        self.cls.private.members.append(Variable(build(Type, "boost::uint64_t").pointer(True).wrap(), "version"))
        get_id = build(Function, "get.id").cls(self.cls).returns(Type("int")).virtual(True).wrap()
        upd = build(Function, "update.version.inc").returns(build(Type, self.cls).pointer(True).wrap()).wrap()
        self.cls.public.methods.append(get_id)
        self.cls.private.methods.append(upd)

    def test_full_featured(self):
        self.cls.config.newline_before_curly_bracket = True
        self.cls.config.indent.class_visibility_specifier = 0
        self.cls.config.linewidth = 100
        decl = to_string(self.cls, self.cls.write_declaration)
        self.assertEqual(_l(decl),
"""\
class MegaManager : public std::thread, boost::noncopyable
{
public:
  virtual int getId();

private:
  MegaManager* updateVersionInc();

  int id;
  boost::uint64_t* version;
};
""")


if __name__ == "__main__":
    sys.exit(unittest.main())
