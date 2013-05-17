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


class ExceptionsHandling(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __createMockedAction(self, name):
        mock = self.mocks.create(name + "Mock")
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def testSimpleFailure(self):
        a, aMock = self.__createMockedAction("a")

        e = Exception("FooBar")
        aMock.expect().andRaise(e)

        with self.assertRaises(CompoundException) as cm:
            a.execute()

        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertIs(cm.exception.exceptions[0], e)
        self.assertEqual(str(cm.exception), "CompoundException: [FooBar]")

        self.assertEqual(a.status, Action.Failed)

    def testExceptionInDependency(self):
        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")

        a.addDependency(b)

        e = Exception()
        bMock.expect().andRaise(e)

        with self.assertRaises(CompoundException) as cm:
            a.execute()

        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertIs(cm.exception.exceptions[0], e)

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Failed)

    def testExceptionsInDependencies_KeepGoing(self):
        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")

        a.addDependency(b)
        a.addDependency(c)
        a.addDependency(d)

        eb = Exception("eb", 42)
        ec = Exception("ec")
        with self.mocks.unordered:
            bMock.expect().andRaise(eb)
            cMock.expect().andRaise(ec)
            dMock.expect()

        with self.assertRaises(CompoundException) as cm:
            a.execute(keepGoing=True)

        self.assertEqual(len(cm.exception.exceptions), 2)
        self.assertIn(eb, cm.exception.exceptions)
        self.assertIn(ec, cm.exception.exceptions)
        self.assertIn(str(cm.exception), ["CompoundException: [('eb', 42), ec]", "CompoundException: [ec, ('eb', 42)]"])

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Failed)
        self.assertEqual(c.status, Action.Failed)
        self.assertEqual(d.status, Action.Successful)

    def testExceptionsInDependencies_NoKeepGoing(self):
        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")

        a.addDependency(b)
        a.addDependency(c)
        a.addDependency(d)

        eb = Exception("eb")
        ec = Exception("ec")
        ed = Exception("ed")
        with self.mocks.unordered:
            with self.mocks.optional:
                bMock.expect().andRaise(eb)
            with self.mocks.optional:
                cMock.expect().andRaise(ec)
            with self.mocks.optional:
                dMock.expect().andRaise(ed)

        with self.assertRaises(CompoundException) as cm:
            a.execute()

        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertIn(cm.exception.exceptions[0], [eb, ec, ed])
        self.assertIn(str(cm.exception), ["CompoundException: [eb]", "CompoundException: [ec]", "CompoundException: [ed]"])

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Canceled]), 2)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Failed]), 1)

    def testExceptionInDependency_BeginEndTimeAnyway(self):
        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")

        a.addDependency(b)

        bMock.expect().andRaise(Exception("eb"))

        with self.assertRaises(CompoundException):
            a.execute()

        self.assertTrue(hasattr(b, "beginTime"))
        self.assertTrue(hasattr(b, "endTime"))
        self.assertTrue(hasattr(a, "beginTime"))
        self.assertTrue(hasattr(a, "endTime"))
