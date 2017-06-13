# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import textwrap
import unittest

from ActionTree import *


class GraphTestCase(unittest.TestCase):
    def test_internal_graph_not_returned(self):
        g = DependencyGraph(Action("a"))
        g1 = g.get_graphviz_graph()
        self.assertEqual(g1.format, "pdf")
        g1.format = "png"
        self.assertEqual(g.get_graphviz_graph().format, "pdf")

    def test_single_action(self):
        a = Action("a")

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
        b = Action("b")
        a = Action("a")
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
        a = Action("a")
        g = DependencyGraph(a)
        a.add_dependency(Action("b"))

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
        for i in range(10):
            a = Action("a")
            b = Action("b")
            b.add_dependency(a)
            c = Action("c")
            c.add_dependency(a)
            d = Action("d")
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
        a = Action(("a", "curious", "label", 42))

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
        a = Action("spaces and; semi=columns")

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
        a = Action(None)

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
        a = Action(None)
        b = Action(None)
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
