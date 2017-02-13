#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

import unittest
from . import FunctionalTestCase


SCHEMA = """
    {
        "title": "Object",
        "type": "object",
        "properties": {
            "id": {
                "type": "integer"
            }
        }
    }
    """


class TestTypes(FunctionalTestCase):
    def test_write_integer(self):
        main_cpp = """
            #include <iostream>
            #include "generated.h"
            int main()
            {
                Object o;
                o.setId(918);
                std::cout << o.toJson() << std::endl;
            }
            """
        expected_stdout = """{"id":918}"""
        self.jcppy(SCHEMA, main_cpp, expected_stdout)

    def test_read_integer(self):
        main_cpp = """
            #include <iostream>
            #include "generated.h"
            int main()
            {
                char json[] = "{\\"id\\":3219}";
                Object o = Object::fromJson(json, sizeof(json));
                std::cout << o.id() << std::endl;
            }
            """
        expected_stdout = "3219"
        self.jcppy(SCHEMA, main_cpp, expected_stdout)
