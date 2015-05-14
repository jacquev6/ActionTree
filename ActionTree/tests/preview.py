# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

from ActionTree import Action


def noop():  # pragma no cover (Test code)
    pass


class PreviewTestCase(unittest.TestCase):
    def test_get_dependencies_and_labels_are_not_only_equal_but_same(self):
        bLabel = ("b",)
        a = Action(noop, "a")
        b = Action(noop, bLabel)
        a.add_dependency(b)

        otherB, = a.get_dependencies()
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def test_simple_preview(self):
        a = Action(noop, "a")
        self.assertEqual(a.get_preview(), ["a"])

    def test_typed_label(self):
        a = Action(noop, ("a", "curious", "label", 42))
        self.assertEqual(a.get_preview(), [("a", "curious", "label", 42)])

    def test_none_label(self):
        a = Action(noop, None)
        self.assertEqual(a.get_preview(), [])

    def test_deep_dependency(self):
        a = Action(noop, "a")
        b = Action(noop, "b")
        c = Action(noop, "c")
        d = Action(noop, "d")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_preview(), ["d", "c", "b", "a"])

    def test_deep_dependency_with_duplicated_label(self):
        a = Action(noop, "label")
        b = Action(noop, "label")
        c = Action(noop, "label")
        d = Action(noop, "label")
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

        a = Action(noop, "a")
        b = Action(noop, "b")
        c = Action(noop, "c")
        d = Action(noop, "d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        self.assertIn(a.get_preview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
