# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


class DependencyCycle(unittest.TestCase):
    def testSelfDependency(self):
        a = Action(lambda: 0, "a")
        with self.assertRaises(Exception) as cm:
            a.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testShortCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        a.addDependency(b)
        with self.assertRaises(Exception) as cm:
            b.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testLongCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        e = Action(lambda: 0, "e")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)
        d.addDependency(e)
        with self.assertRaises(Exception) as cm:
            e.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
