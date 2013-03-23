# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import Framework


class DependencyCycle(Framework.TestCase):
    def testSelfDependency(self):
        with self.assertRaises(Exception):
            self.addDependency("a", "a")

    def testShortCycle(self):
        self.addDependency("a", "b")
        with self.assertRaises(Exception):
            self.addDependency("b", "a")

    def testLongCycle(self):
        self.addDependency("a", "b")
        self.addDependency("b", "c")
        self.addDependency("c", "d")
        self.addDependency("d", "e")
        with self.assertRaises(Exception):
            self.addDependency("e", "a")
