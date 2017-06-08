# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class PreviewTestCase(unittest.TestCase):
    def test_dependencies_and_labels_are_not_only_equal_but_same(self):
        bLabel = ("b",)
        a = Action("a")
        b = Action(bLabel)
        a.add_dependency(b)

        otherB, = a.dependencies
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def test_simple_preview(self):
        a = Action("a")
        self.assertEqual(a.get_preview(), ["a"])

    def test_preview_twice(self):
        # There was a bug where a second call to get_possible_execution_order would return [] :-/
        a = Action("a")
        self.assertEqual(a.get_preview(), ["a"])
        self.assertEqual(a.get_preview(), ["a"])

    def test_typed_label(self):
        a = Action(("a", "curious", "label", 42))
        self.assertEqual(a.get_preview(), [("a", "curious", "label", 42)])

    def test_none_label(self):
        a = Action(None)
        self.assertEqual(a.get_preview(), [None])

    def test_deep_dependency(self):
        a = Action("a")
        b = Action("b")
        c = Action("c")
        d = Action("d")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_preview(), ["d", "c", "b", "a"])

    def test_deep_dependency_with_duplicated_label(self):
        a = Action("label")
        b = Action("label")
        c = Action("label")
        d = Action("label")
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

        a = Action("a")
        b = Action("b")
        c = Action("c")
        d = Action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        self.assertIn(a.get_preview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
