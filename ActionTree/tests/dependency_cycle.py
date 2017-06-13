# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class DependencyCycleTestCase(unittest.TestCase):
    def test_self_dependency(self):
        a = Action("a")
        with self.assertRaises(Exception) as cm:
            a.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_short_cycle(self):
        a = Action("a")
        b = Action("b")
        a.add_dependency(b)
        with self.assertRaises(Exception) as cm:
            b.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_long_cycle(self):
        a = Action("a")
        b = Action("b")
        c = Action("c")
        d = Action("d")
        e = Action("e")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        with self.assertRaises(Exception) as cm:
            e.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
