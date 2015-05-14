# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


class PreviewTestCase(unittest.TestCase):
    def test_dependencies_and_labels_are_not_only_equal_but_same(self):
        bLabel = ("b",)
        a = Action(None, "a")
        b = Action(None, bLabel)
        a.add_dependency(b)

        otherB, = a.dependencies
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def test_simple_preview(self):
        a = Action(None, "a")
        self.assertEqual(a.get_preview(), ["a"])

    def test_typed_label(self):
        a = Action(None, ("a", "curious", "label", 42))
        self.assertEqual(a.get_preview(), [("a", "curious", "label", 42)])

    def test_none_label(self):
        a = Action(None, None)
        self.assertEqual(a.get_preview(), [])

    def test_deep_dependency(self):
        a = Action(None, "a")
        b = Action(None, "b")
        c = Action(None, "c")
        d = Action(None, "d")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_preview(), ["d", "c", "b", "a"])

    def test_deep_dependency_with_duplicated_label(self):
        a = Action(None, "label")
        b = Action(None, "label")
        c = Action(None, "label")
        d = Action(None, "label")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_preview(), ["label", "label", "label", "label"])

    def test_diamond_dependency(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a = Action(None, "a")
        b = Action(None, "b")
        c = Action(None, "c")
        d = Action(None, "d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        self.assertIn(a.get_preview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
