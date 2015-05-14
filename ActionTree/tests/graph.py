# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import collections
import textwrap
import unittest

from ActionTree.drawings import make_graph


MockAction = collections.namedtuple("MockAction", "label, dependencies")


class GraphTestCase(unittest.TestCase):
    def test_single_action(self):
        a = MockAction("a", [])

        self.assertEqual(
            make_graph(a).source,
            textwrap.dedent("""\
                digraph action {
                \tnode [shape=box]
                \t\t0 [label=a]
                }"""
            )
        )

    def test_dependency(self):
        b = MockAction("b", [])
        a = MockAction("a", [b])

        self.assertEqual(
            make_graph(a).source,
            textwrap.dedent("""\
                digraph action {
                \tnode [shape=box]
                \t\t0 [label=a]
                \t\t1 [label=b]
                \t\t\t0 -> 1
                }"""
            )
        )

    def test_diamond(self):
        a = MockAction("a", [])
        b = MockAction("b", [a])
        c = MockAction("c", [a])
        d = MockAction("d", [b, c])

        self.assertEqual(
            make_graph(d).source,
            textwrap.dedent("""\
                digraph action {
                \tnode [shape=box]
                \t\t0 [label=d]
                \t\t1 [label=b]
                \t\t2 [label=a]
                \t\t\t1 -> 2
                \t\t\t0 -> 1
                \t\t3 [label=c]
                \t\t\t3 -> 2
                \t\t\t0 -> 3
                }"""
            )
        )

    def test_weird_label(self):
        a = MockAction("spaces and; semi=columns", [])

        self.assertEqual(
            make_graph(a).source,
            textwrap.dedent("""\
                digraph action {
                \tnode [shape=box]
                \t\t0 [label="spaces and; semi=columns"]
                }"""
            )
        )
