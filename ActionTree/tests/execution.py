# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class ExecutionTestCase(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        mock.side_effect = lambda: self.calls.append(name)
        action = ActionFromCallable(mock, name)
        return action, mock

    def test_simple_execution(self):
        a, aMock = self.__create_mocked_action("a")

        report = execute(a)

        self.assertTrue(report.is_success)
        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Successful)

        aMock.assert_called_once_with()

        self.assertEqual(self.calls, ["a"])

    def test_many_dependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        execute(a)

        aMock.assert_called_once_with()
        bMock.assert_called_once_with()
        cMock.assert_called_once_with()
        dMock.assert_called_once_with()

        self.assertEqual(self.calls[3:], ["a"])
        self.assertEqual(sorted(self.calls[:3]), ["b", "c", "d"])

    def test_deep_dependencies(self):
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

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        e, eMock = self.__create_mocked_action("e")
        f, fMock = self.__create_mocked_action("f")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        e.add_dependency(f)

        execute(a)

        aMock.assert_called_once_with()
        bMock.assert_called_once_with()
        cMock.assert_called_once_with()
        dMock.assert_called_once_with()
        eMock.assert_called_once_with()
        fMock.assert_called_once_with()

        self.assertEqual(self.calls, ["f", "e", "d", "c", "b", "a"])

    def test_diamond_dependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        execute(a)

        self.assertEqual(self.calls[0:1], ["d"])
        self.assertEqual(sorted(self.calls[1:3]), ["b", "c"])
        self.assertEqual(self.calls[3:], ["a"])

    def test_half_diamond_dependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(d)
        b.add_dependency(d)

        execute(a)

        self.assertEqual(self.calls, ["d", "b", "a"])

    def test_two_deep_branches(self):
        #     a
        #    / \
        #   b   c
        #   |   |
        #   d   e

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        e, eMock = self.__create_mocked_action("e")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(e)

        execute(a)

        aMock.assert_called_once_with()
        bMock.assert_called_once_with()
        cMock.assert_called_once_with()
        dMock.assert_called_once_with()
        eMock.assert_called_once_with()

        self.assertIn(
            self.calls,
            [
                # Leaves first
                ["d", "e", "b", "c", "a"],
                ["e", "d", "b", "c", "a"],
                ["d", "e", "c", "b", "a"],
                ["e", "d", "c", "b", "a"],
                # Full branch first
                ["d", "b", "e", "c", "a"],
                ["e", "c", "d", "b", "a"],
                # Leave, then full branch
                ["e", "d", "b", "c", "a"],
                ["d", "e", "c", "b", "a"],
            ]
        )
