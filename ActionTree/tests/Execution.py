# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import threading
import time
import unittest
import MockMockMock

from ActionTree import Action


class Execution(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __createMockedAction(self, name):
        mock = self.mocks.create(name + "Mock")
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def testSimpleExecution(self):
        a, aMock = self.__createMockedAction("a")

        aMock.expect()

        self.assertEqual(a.status, Action.Pending)
        a.execute()
        self.assertEqual(a.status, Action.Successful)

    def testManyDependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(c)
        a.addDependency(d)

        with self.mocks.unordered:
            bMock.expect()
            cMock.expect()
            dMock.expect()
        aMock.expect()

        a.execute()

    def testDeepDependencies(self):
        #  a
        #  |
        #  b
        #  |
        #  c
        #  |
        #  d
        #  |
        #  e
        #  |
        #  f

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        e, eMock = self.__createMockedAction("e")
        f, fMock = self.__createMockedAction("f")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)
        d.addDependency(e)
        e.addDependency(f)

        fMock.expect()
        eMock.expect()
        dMock.expect()
        cMock.expect()
        bMock.expect()
        aMock.expect()

        a.execute()

    def testDiamondDependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(c)
        b.addDependency(d)
        c.addDependency(d)

        dMock.expect()
        with self.mocks.unordered:
            bMock.expect()
            cMock.expect()
        aMock.expect()

        a.execute()

    def testHalfDiamondDependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(d)
        b.addDependency(d)

        dMock.expect()
        bMock.expect()
        aMock.expect()

        a.execute()

    def testTwoDeepBranches(self):
        #     a
        #    / \
        #   b   c
        #   |   |
        #   d   e

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        e, eMock = self.__createMockedAction("e")
        a.addDependency(b)
        a.addDependency(c)
        b.addDependency(d)
        c.addDependency(e)

        with self.mocks.unordered:
            dMock.expect()
            eMock.expect()
        # In previous implementation in ViDE, deepest leaves were
        # executed first. It is not mandatory, but it make cleaner
        # executions, because similar tasks are executed at once.
        # To restore this behavior if needed, uncomment next line
        # with self.mocks.unordered:
        # This would have to be done also in getPreview
            bMock.expect()
            cMock.expect()
        aMock.expect()

        a.execute()
