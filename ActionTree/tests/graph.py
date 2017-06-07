# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import collections
import textwrap
import unittest

from ActionTree.drawings import *


MockAction = collections.namedtuple("MockAction", "label, dependencies, begin_time, end_time, status")


def mock_action(label, dependencies):
    return MockAction(label, dependencies, None, None, None)


class GraphTestCase(unittest.TestCase):
    def setUp(self):
        self.previous_sorted = DependencyGraph._sorted
        DependencyGraph._sorted = sorted

    def tearDown(self):
        DependencyGraph._sorted = self.previous_sorted

    def test_single_action(self):
        a = mock_action("a", [])

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=a]
                }"""
            )
        )

    def test_dependency(self):
        b = mock_action("b", [])
        a = mock_action("a", [b])

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t1 [label=a]
                \t0 [label=b]
                \t\t1 -> 0
                }"""
            )
        )

    def test_diamond(self):
        a = mock_action("a", [])
        b = mock_action("b", [a])
        c = mock_action("c", [a])
        d = mock_action("d", [b, c])

        self.assertEqual(
            DependencyGraph(d).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=a]
                \t1 [label=b]
                \t2 [label=c]
                \t3 [label=d]
                \t\t1 -> 0
                \t\t2 -> 0
                \t\t3 -> 1
                \t\t3 -> 2
                }"""
            )
        )

    def test_weird_label(self):
        a = mock_action("spaces and; semi=columns", [])

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label="spaces and; semi=columns"]
                }"""
            )
        )
