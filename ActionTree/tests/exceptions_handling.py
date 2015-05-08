# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest
import MockMockMock

from ActionTree import Action, CompoundException


class ExceptionsHandling(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __create_mocked_action(self, name):
        mock = self.mocks.create(name)
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def test_simple_failure(self):
        a, aMock = self.__create_mocked_action("a")

        e = Exception("FooBar")
        aMock.expect().andRaise(e)

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(catcher.exception.exceptions, [e])
        self.assertEqual(a.status, Action.Failed)

    def test_exception_in_dependency(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")

        a.add_dependency(b)

        e = Exception()
        bMock.expect().andRaise(e)

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertIs(catcher.exception.exceptions[0], e)

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Failed)

    def test_exceptions_in_dependencies_with_keep_going(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")

        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        eb = Exception("eb", 42)
        ec = Exception("ec")
        with self.mocks.unordered:
            bMock.expect().andRaise(eb)
            cMock.expect().andRaise(ec)
            dMock.expect()

        with self.assertRaises(CompoundException) as catcher:
            a.execute(keep_going=True)

        self.assertEqual(len(catcher.exception.exceptions), 2)
        self.assertIn(eb, catcher.exception.exceptions)
        self.assertIn(ec, catcher.exception.exceptions)

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Failed)
        self.assertEqual(c.status, Action.Failed)
        self.assertEqual(d.status, Action.Successful)

    def test_exceptions_in_dependencies_without_keep_going(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")

        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

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

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertIn(catcher.exception.exceptions[0], [eb, ec, ed])

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Canceled]), 2)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Failed]), 1)

    def test_exception_in_dependency_populates_begin_end_time_anyway(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")

        a.add_dependency(b)

        bMock.expect().andRaise(Exception("eb"))

        with self.assertRaises(CompoundException):
            a.execute()

        self.assertTrue(hasattr(b, "begin_time"))
        self.assertTrue(hasattr(b, "end_time"))
        self.assertTrue(hasattr(a, "begin_time"))
        self.assertTrue(hasattr(a, "end_time"))
