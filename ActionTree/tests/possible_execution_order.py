# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class PreviewTestCase(unittest.TestCase):
    def test_dependencies_and_labels_are_not_only_equal_but_same(self):
        bLabel = ("b",)
        a = Action("a")
        b = Action(bLabel)
        a.add_dependency(b)

        (otherB,) = a.dependencies
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def test_simple_preview(self):
        a = Action("a")
        self.assertEqual(a.get_possible_execution_order(), [a])

    def test_preview_twice(self):
        # There was a bug where a second call to get_possible_execution_order would return [] :-/
        a = Action("a")
        self.assertEqual(a.get_possible_execution_order(), [a])
        self.assertEqual(a.get_possible_execution_order(), [a])

    def test_deep_dependency(self):
        a = Action("a")
        b = Action("b")
        c = Action("c")
        d = Action("d")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)

        self.assertEqual(a.get_possible_execution_order(), [d, c, b, a])

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

        self.assertEqual(a.get_possible_execution_order(), [d, b, c, a])
