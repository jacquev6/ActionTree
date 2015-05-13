# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest
import MockMockMock

from ActionTree.drawings import ActionGraph


class GraphTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()
        self.mocks.unordered  # @todo in MockMockMock, find a better syntax to use grouping without "with" keyword

    def tearDown(self):
        self.mocks.tearDown()
        unittest.TestCase.tearDown(self)

    def __create_mocked_action(self, name, label, dependencies):
        a = self.mocks.create(name)
        a.expect.label.andReturn(label)
        a.expect.getDependencies().andReturn(dependencies)
        return a.object

    def __assert_graph_equal(self, a, g):
        self.assertEqual(ActionGraph(a).dotString(), g)

    def test_single_action(self):
        a = self.__create_mocked_action("a", "a", [])

        self.__assert_graph_equal(a, 'digraph "action" {node [shape="box"];0[label="a"];}')

    def test_dependency(self):
        b = self.__create_mocked_action("b", "b", [])
        a = self.__create_mocked_action("a", "a", [b])

        self.__assert_graph_equal(a, 'digraph "action" {node [shape="box"];0[label="a"];1[label="b"];0->1;}')

    def test_diamond(self):
        a = self.__create_mocked_action("a", "a", [])
        b = self.__create_mocked_action("b", "b", [a])
        c = self.__create_mocked_action("c", "c", [a])
        d = self.__create_mocked_action("d", "d", [b, c])

        self.__assert_graph_equal(d, 'digraph "action" {node [shape="box"];0[label="d"];1[label="b"];2[label="a"];3[label="c"];0->1;0->3;1->2;3->2;}')
