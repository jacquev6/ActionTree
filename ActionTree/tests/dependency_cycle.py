# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


class DependencyCycle(unittest.TestCase):
    def testSelfDependency(self):
        a = Action(lambda: 0, "a")
        with self.assertRaises(Exception) as cm:
            a.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testShortCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        a.add_dependency(b)
        with self.assertRaises(Exception) as cm:
            b.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testLongCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        e = Action(lambda: 0, "e")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        with self.assertRaises(Exception) as cm:
            e.add_dependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
