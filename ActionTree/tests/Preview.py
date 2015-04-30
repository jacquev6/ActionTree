# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


class Preview(unittest.TestCase):
    def testGetDependenciesAndLabelsAreNotOnlyEqualButSame(self):
        bLabel = ("b",)
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, bLabel)
        a.addDependency(b)

        otherB, = a.getDependencies()
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def testSimplePreview(self):
        a = Action(lambda: 0, "a")
        self.assertEqual(a.getPreview(), ["a"])

    def testTypedLabel(self):
        a = Action(lambda: 0, ("a", "curious", "label", 42))
        self.assertEqual(a.getPreview(), [("a", "curious", "label", 42)])

    def testNoneLabel(self):
        a = Action(lambda: 0, None)
        self.assertEqual(a.getPreview(), [])

    def testDeepDependency(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)

        self.assertEqual(a.getPreview(), ["d", "c", "b", "a"])

    def testDeepDependencyWithDuplicatedLabel(self):
        a = Action(lambda: 0, "label")
        b = Action(lambda: 0, "label")
        c = Action(lambda: 0, "label")
        d = Action(lambda: 0, "label")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)

        self.assertEqual(a.getPreview(), ["label", "label", "label", "label"])

    def testDiamondDependency(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.addDependency(b)
        a.addDependency(c)
        b.addDependency(d)
        c.addDependency(d)

        self.assertIn(a.getPreview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
