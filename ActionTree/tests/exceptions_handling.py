# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import ActionFromCallable as Action, CompoundException


class ExceptionsHandlingTestCase(unittest.TestCase):
    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        action = Action(mock, name)
        return action, mock

    def test_simple_failure(self):
        a, aMock = self.__create_mocked_action("a")

        e = Exception("FooBar")
        aMock.side_effect = e

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(catcher.exception.exceptions, [e])

        aMock.assert_called_once_with()

        self.assertEqual(a.status, Action.Failed)

    def test_exception_in_dependency(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")

        a.add_dependency(b)

        e = Exception()
        bMock.side_effect = e

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertIs(catcher.exception.exceptions[0], e)

        bMock.assert_called_once_with()
        aMock.assert_not_called()

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
        bMock.side_effect = eb
        cMock.side_effect = ec

        with self.assertRaises(CompoundException) as catcher:
            a.execute(keep_going=True)

        self.assertEqual(len(catcher.exception.exceptions), 2)
        self.assertIn(eb, catcher.exception.exceptions)
        self.assertIn(ec, catcher.exception.exceptions)

        aMock.assert_not_called()
        bMock.assert_called_once_with()
        cMock.assert_called_once_with()
        dMock.assert_called_once_with()

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Failed)
        self.assertEqual(c.status, Action.Failed)
        self.assertEqual(d.status, Action.Successful)

    def test_exceptions_in_long_branch_dependencies_with_keep_going(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        e, eMock = self.__create_mocked_action("e")
        f, fMock = self.__create_mocked_action("f")
        g, gMock = self.__create_mocked_action("g")

        a.add_dependency(b)
        b.add_dependency(c)
        a.add_dependency(d)
        d.add_dependency(e)
        a.add_dependency(f)
        f.add_dependency(g)

        ex = Exception()
        eMock.side_effect = ex

        with self.assertRaises(CompoundException) as catcher:
            a.execute(keep_going=True)

        self.assertEqual(catcher.exception.exceptions, [ex])

        aMock.assert_not_called()
        bMock.assert_called_once_with()
        cMock.assert_called_once_with()
        dMock.assert_not_called()
        eMock.assert_called_once_with()
        fMock.assert_called_once_with()
        gMock.assert_called_once_with()

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(b.status, Action.Successful)
        self.assertEqual(c.status, Action.Successful)
        self.assertEqual(d.status, Action.Canceled)
        self.assertEqual(e.status, Action.Failed)
        self.assertEqual(f.status, Action.Successful)
        self.assertEqual(g.status, Action.Successful)

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
        bMock.side_effect = eb
        cMock.side_effect = ec
        dMock.side_effect = ed

        with self.assertRaises(CompoundException) as catcher:
            a.execute()

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertIn(catcher.exception.exceptions[0], [eb, ec, ed])

        aMock.assert_not_called()
        self.assertEqual(bMock.called + cMock.called + dMock.called, 1)

        self.assertEqual(a.status, Action.Canceled)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Canceled]), 2)
        self.assertEqual(len([x for x in [b, c, d] if x.status == Action.Failed]), 1)

    def test_exception_in_dependency_populates_begin_end_time_anyway(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")

        a.add_dependency(b)

        bMock.side_effect = Exception("eb")

        with self.assertRaises(CompoundException):
            a.execute()

        aMock.assert_not_called()
        bMock.assert_called_once_with()

        self.assertTrue(hasattr(b, "begin_time"))
        self.assertTrue(hasattr(b, "end_time"))
        self.assertTrue(hasattr(a, "begin_time"))
        self.assertTrue(hasattr(a, "end_time"))
