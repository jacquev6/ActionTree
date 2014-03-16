# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import MockMockMock
import AnotherPyGraphvizAgain.Raw as gv

from ActionTree.Drawings import ActionGraph


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
