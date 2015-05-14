# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


def noop():  # pragma no cover (Test code)
    pass


class DependencyCycleTestCase(unittest.TestCase):
    def test_self_dependency(self):
        a = Action(noop, "a")
        with self.assertRaises(Exception) as cm:
            a.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_short_cycle(self):
        a = Action(noop, "a")
        b = Action(noop, "b")
        a.add_dependency(b)
        with self.assertRaises(Exception) as cm:
            b.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def test_long_cycle(self):
        a = Action(noop, "a")
        b = Action(noop, "b")
        c = Action(noop, "c")
        d = Action(noop, "d")
        e = Action(noop, "e")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        with self.assertRaises(Exception) as cm:
            e.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
