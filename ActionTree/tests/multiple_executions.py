# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class MultipleExecutionsTestCase(unittest.TestCase):
    REPEAT = 5

    def setUp(self):
        self.calls = []

    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        mock.side_effect = lambda: self.calls.append(name)
        action = ActionFromCallable(mock, name)
        return action, mock

    def test_simple_success(self):
        a, aMock = self.__create_mocked_action("a")

        for i in range(self.REPEAT):
            report = execute(a)
            self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Successful)

        call = unittest.mock.call
        self.assertEqual(aMock.mock_calls, [call()] * self.REPEAT)

        self.assertEqual(self.calls, ["a"] * self.REPEAT)

    def test_failure_in_middle(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        a.add_dependency(b)
        b.add_dependency(c)

        # A lambda that make a side effect then raises an exception
        bMock.side_effect = lambda: [self.calls.append("b"), 1 / 0]

        for i in range(self.REPEAT):
            with self.assertRaises(CompoundException) as catcher:
                execute(a)
            report = catcher.exception.execution_report
            self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
            self.assertEqual(report.get_action_status(b).status, ExecutionReport.ActionStatus.Failed)
            self.assertEqual(report.get_action_status(c).status, ExecutionReport.ActionStatus.Successful)

        call = unittest.mock.call
        self.assertEqual(aMock.mock_calls, [])
        self.assertEqual(bMock.mock_calls, [call()] * self.REPEAT)
        self.assertEqual(cMock.mock_calls, [call()] * self.REPEAT)

        self.assertEqual(self.calls, ["c", "b"] * self.REPEAT)
