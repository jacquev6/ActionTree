# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


class Preview(unittest.TestCase):
    def test_get_dependencies_and_labels_are_not_only_equal_but_same(self):
        bLabel = ("b",)
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, bLabel)
        a.add_dependency(b)

        otherB, = a.get_dependencies()
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def test_simple_preview(self):
        a = Action(lambda: 0, "a")
        self.assertEqual(a.get_preview(), ["a"])

    def test_typed_label(self):
        a = Action(lambda: 0, ("a", "curious", "label", 42))
        self.assertEqual(a.get_preview(), [("a", "curious", "label", 42)])

    def test_none_label(self):
        a = Action(lambda: 0, None)
        self.assertEqual(a.get_preview(), [])

    def test_deep_dependency(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_preview(), ["d", "c", "b", "a"])

    def test_deep_dependency_with_duplicated_label(self):
        a = Action(lambda: 0, "label")
        b = Action(lambda: 0, "label")
        c = Action(lambda: 0, "label")
        d = Action(lambda: 0, "label")
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

        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        self.assertIn(a.get_preview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
