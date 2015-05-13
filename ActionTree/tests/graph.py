# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest
import MockMockMock
import AnotherPyGraphvizAgain.Raw as gv

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
        self.assertEqual(ActionGraph(a).dotString(), g.dotString())

    def __create_empty_graph(self):
        g = gv.Graph("action")
        g.nodeAttr.set("shape", "box")
        return g

    def __createNode(self, id, name):
        return gv.Node(str(id)).set("label", name)

    def test_single_action(self):
        a = self.__create_mocked_action("a", "a", [])

        g = self.__create_empty_graph()
        aN = self.__createNode(0, "a")
        g.add(aN)

        self.__assert_graph_equal(a, g)

    def test_dependency(self):
        b = self.__create_mocked_action("b", "b", [])
        a = self.__create_mocked_action("a", "a", [b])

        aN = self.__createNode(0, "a")
        bN = self.__createNode(1, "b")
        g = self.__create_empty_graph()
        g.add(aN).add(bN)
        g.add(gv.Link(aN, bN))

        self.__assert_graph_equal(a, g)

    def test_diamond(self):
        a = self.__create_mocked_action("a", "a", [])
        b = self.__create_mocked_action("b", "b", [a])
        c = self.__create_mocked_action("c", "c", [a])
        d = self.__create_mocked_action("d", "d", [b, c])

        g = self.__create_empty_graph()
        aN = self.__createNode(2, "a")
        bN = self.__createNode(1, "b")
        cN = self.__createNode(3, "c")
        dN = self.__createNode(0, "d")
        g.add(aN).add(bN).add(cN).add(dN)
        g.add(gv.Link(bN, aN)).add(gv.Link(cN, aN))
        g.add(gv.Link(dN, bN)).add(gv.Link(dN, cN))

        self.__assert_graph_equal(d, g)
