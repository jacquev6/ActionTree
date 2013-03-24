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

from ActionTree import Action, CompoundException


class MultipleExecutions(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __createMockedAction(self, name):
        mock = self.mocks.create(name + "Mock")
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def testSimpleSuccess(self):
        repeat = 5
        a, aMock = self.__createMockedAction("a")

        for i in range(repeat):
            aMock.expect()

        for i in range(repeat):
            a.execute()
            self.assertEqual(a.status, Action.Successful)

    def testFailureInMiddle(self):
        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        a.addDependency(b)
        b.addDependency(c)

        repeat = 5
        for i in range(repeat):
            cMock.expect()
            bMock.expect().andRaise(Exception())

        for i in range(repeat):
            with self.assertRaises(CompoundException):
                a.execute()
            self.assertEqual(a.status, Action.Canceled)
            self.assertEqual(b.status, Action.Failed)
            self.assertEqual(c.status, Action.Successful)
