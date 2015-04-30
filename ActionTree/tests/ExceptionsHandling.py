# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

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
