# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest
import MockMockMock
import AnotherPyGraphvizAgain.Raw as gv

from ActionTree.drawings import ActionGraph


class Graph(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.actionMocks = MockMockMock.Engine()
        self.actionMocks.unordered  # @todo in MockMockMock, find a better syntax to use grouping without "with" keyword

    def tearDown(self):
        self.actionMocks.tearDown()
        unittest.TestCase.tearDown(self)

    def __createMockedAction(self, name, label, dependencies):
        a = self.actionMocks.create(name)
        a.expect.label.andReturn(label)
        a.expect.getDependencies().andReturn(dependencies)
        return a.object

    def __assertGraphEqual(self, a, g):
        self.assertEqual(ActionGraph(a).dotString(), g.dotString())

    def __createEmptyGraph(self):
        g = gv.Graph("action")
        g.nodeAttr.set("shape", "box")
        return g

    def __createNode(self, id, name):
        return gv.Node(str(id)).set("label", name)

    def testSingleAction(self):
        a = self.__createMockedAction("a", "a", [])

        g = self.__createEmptyGraph()
        aN = self.__createNode(0, "a")
        g.add(aN)

        self.__assertGraphEqual(a, g)

    def testDependency(self):
        b = self.__createMockedAction("b", "b", [])
        a = self.__createMockedAction("a", "a", [b])

        aN = self.__createNode(0, "a")
        bN = self.__createNode(1, "b")
        g = self.__createEmptyGraph()
        g.add(aN).add(bN)
        g.add(gv.Link(aN, bN))

        self.__assertGraphEqual(a, g)

    def testDiamond(self):
        a = self.__createMockedAction("a", "a", [])
        b = self.__createMockedAction("b", "b", [a])
        c = self.__createMockedAction("c", "c", [a])
        d = self.__createMockedAction("d", "d", [b, c])

        g = self.__createEmptyGraph()
        aN = self.__createNode(2, "a")
        bN = self.__createNode(1, "b")
        cN = self.__createNode(3, "c")
        dN = self.__createNode(0, "d")
        g.add(aN).add(bN).add(cN).add(dN)
        g.add(gv.Link(bN, aN)).add(gv.Link(cN, aN))
        g.add(gv.Link(dN, bN)).add(gv.Link(dN, cN))

        self.__assertGraphEqual(d, g)
