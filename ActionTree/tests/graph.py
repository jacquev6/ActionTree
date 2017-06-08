# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import textwrap
import unittest

from ActionTree import *


class GraphTestCase(unittest.TestCase):
    def test_internal_graph_not_returned(self):
        g = DependencyGraph(ActionFromCallable(None, "a"))
        g1 = g.get_graphviz_graph()
        self.assertEqual(g1.format, "pdf")
        g1.format = "png"
        self.assertEqual(g.get_graphviz_graph().format, "pdf")

    def test_single_action(self):
        a = ActionFromCallable(None, "a")

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
        b = ActionFromCallable(None, "b")
        a = ActionFromCallable(None, "a")
        a.add_dependency(b)

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=b]
                \t1 [label=a]
                \t\t1 -> 0
                }"""
            )
        )

    def test_add_dependency_after_constructing_graph(self):
        a = ActionFromCallable(None, "a")
        g = DependencyGraph(a)
        a.add_dependency(ActionFromCallable(None, "b"))

        self.assertEqual(
            g.get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=a]
                }"""
            )
        )

    def test_diamond(self):
        for i in range(1000):
            a = ActionFromCallable(None, "a")
            b = ActionFromCallable(None, "b")
            b.add_dependency(a)
            c = ActionFromCallable(None, "c")
            c.add_dependency(a)
            d = ActionFromCallable(None, "d")
            d.add_dependency(c)
            d.add_dependency(b)

            self.assertIn(
                DependencyGraph(d).get_graphviz_graph().source,
                [
                    textwrap.dedent(
                        """\
                        digraph action {
                        \tnode [shape=box]
                        \t0 [label=a]
                        \t1 [label=b]
                        \t\t1 -> 0
                        \t2 [label=c]
                        \t\t2 -> 0
                        \t3 [label=d]
                        \t\t3 -> 1
                        \t\t3 -> 2
                        }"""
                    ),
                    textwrap.dedent(
                        """\
                        digraph action {
                        \tnode [shape=box]
                        \t0 [label=a]
                        \t1 [label=c]
                        \t\t1 -> 0
                        \t2 [label=b]
                        \t\t2 -> 0
                        \t3 [label=d]
                        \t\t3 -> 1
                        \t\t3 -> 2
                        }"""
                    ),
                ]
            )

    def test_typed_label(self):
        a = ActionFromCallable(None, ("a", "curious", "label", 42))

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label="('a', 'curious', 'label', 42)"]
                }"""
            )
        )

    def test_weird_string_label(self):
        a = ActionFromCallable(None, "spaces and; semi=columns")

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

    def test_None_label(self):
        a = ActionFromCallable(None, None)

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=None]
                }"""
            )
        )

    def test_None_label_twice(self):
        a = ActionFromCallable(None, None)
        b = ActionFromCallable(None, None)
        a.add_dependency(b)

        self.assertEqual(
            DependencyGraph(a).get_graphviz_graph().source,
            textwrap.dedent(
                """\
                digraph action {
                \tnode [shape=box]
                \t0 [label=None]
                \t1 [label=None]
                \t\t1 -> 0
                }"""
            )
        )
