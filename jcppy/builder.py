#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details)

class Builder(object):
    def __init__(self, cls, *args, **kwargs):
        self._cls = cls
        self._instance = cls(*args, **kwargs)

    def __getattr__(self, name):
        class _Attribute(object):
            def __init__(self, builder, instance, attr):
                self._builder = builder
                self._instance = instance
                self._attr = attr

            def __call__(self, value):
                setattr(self._instance, self._attr, value)
                return self._builder

        return _Attribute(self, self._instance, name)

    def wrap(self):
        return self._instance


def build(cls, *args, **kwargs):
    return Builder(cls, *args, **kwargs)
