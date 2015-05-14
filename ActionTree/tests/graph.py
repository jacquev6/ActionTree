# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import textwrap

from ActionTree.drawings import make_graph
from . import TestCaseWithMocks


class GraphTestCase(TestCaseWithMocks):
    def setUp(self):
        super(GraphTestCase, self).setUp()
        self.mocks.unordered  # @todo in MockMockMock, find a better syntax to use grouping without "with" keyword

    def __create_mocked_action(self, name, label, dependencies):
        # @todo Use namedtuples instead of mocks
        a = self.mocks.create(name)
        a.expect.label.andReturn(label)
        a.expect.dependencies.andReturn(dependencies)
        return a.object

    def __assert_graph_equal(self, a, g):
        self.assertEqual(make_graph(a).source, g)

    def test_single_action(self):
        a = self.__create_mocked_action("a", "a", [])

        self.__assert_graph_equal(a, textwrap.dedent("""\
            digraph action {
            \tnode [shape=box]
            \t\t0 [label=a]
            }"""))

    def test_dependency(self):
        b = self.__create_mocked_action("b", "b", [])
        a = self.__create_mocked_action("a", "a", [b])

        self.__assert_graph_equal(a, textwrap.dedent("""\
            digraph action {
            \tnode [shape=box]
            \t\t0 [label=a]
            \t\t1 [label=b]
            \t\t\t0 -> 1
            }"""))

    def test_diamond(self):
        a = self.__create_mocked_action("a", "a", [])
        b = self.__create_mocked_action("b", "b", [a])
        c = self.__create_mocked_action("c", "c", [a])
        d = self.__create_mocked_action("d", "d", [b, c])

        self.__assert_graph_equal(d, textwrap.dedent("""\
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
            }"""))
