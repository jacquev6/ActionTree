# coding: utf8

# Copyright 2017-2018 Vincent Jacques <vincent@vincent-jacques.net>


import re
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

    spaces = re.compile(r"\s+")

    def normalize(self, g):
        return self.spaces.sub(" ", g).strip()

    def assertGraphEqual(self, g, expected):
        self.assertEqual(
            self.normalize(g.source),
            self.normalize(expected),
        )

    def test_single_action(self):
        a = Action("a")

        self.assertGraphEqual(
            DependencyGraph(a).get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [label=a]
            }
            """
        )

    def test_dependency(self):
        b = Action("b")
        a = Action("a")
        a.add_dependency(b)

        self.assertGraphEqual(
            DependencyGraph(a).get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [label=b]
                1 [label=a]
                1 -> 0
            }
            """
        )

    def test_add_dependency_after_constructing_graph(self):
        a = Action("a")
        g = DependencyGraph(a)
        a.add_dependency(Action("b"))

        self.assertGraphEqual(
            g.get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [label=a]
            }
            """
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
                self.normalize(DependencyGraph(d).get_graphviz_graph().source),
                [
                    self.normalize(
                        """
                        digraph action {
                            node [shape=box]
                            0 [label=a]
                            1 [label=b]
                            1 -> 0
                            2 [label=c]
                            2 -> 0
                            3 [label=d]
                            3 -> 1
                            3 -> 2
                        }
                        """
                    ),
                    self.normalize(
                        """
                        digraph action {
                            node [shape=box]
                            0 [label=a]
                            1 [label=c]
                            1 -> 0
                            2 [label=b]
                            2 -> 0
                            3 [label=d]
                            3 -> 1
                            3 -> 2
                        }
                        """
                    ),
                ]
            )

    def test_weird_string_label(self):
        a = Action("spaces and; semi=columns")

        self.assertGraphEqual(
            DependencyGraph(a).get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [label="spaces and; semi=columns"]
            }
            """
        )

    def test_None_label(self):
        a = Action(None)

        self.assertGraphEqual(
            DependencyGraph(a).get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [shape=point]
            }
            """
        )

    def test_None_label_twice(self):
        a = Action(None)
        b = Action(None)
        a.add_dependency(b)

        self.assertGraphEqual(
            DependencyGraph(a).get_graphviz_graph(),
            """
            digraph action {
                node [shape=box]
                0 [shape=point]
                1 [shape=point]
                1 -> 0
            }
            """
        )
