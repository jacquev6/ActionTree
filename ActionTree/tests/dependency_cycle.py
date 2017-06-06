# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import Action


class DependencyCycleTestCase(unittest.TestCase):
    def test_self_dependency(self):
        a = Action(None, "a")
        with self.assertRaises(Exception) as cm:
            a.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_short_cycle(self):
        a = Action(None, "a")
        b = Action(None, "b")
        a.add_dependency(b)
        with self.assertRaises(Exception) as cm:
            b.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_long_cycle(self):
        a = Action(None, "a")
        b = Action(None, "b")
        c = Action(None, "c")
        d = Action(None, "d")
        e = Action(None, "e")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        with self.assertRaises(Exception) as cm:
            e.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
