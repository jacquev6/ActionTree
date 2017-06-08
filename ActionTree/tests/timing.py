# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *


class Counter:
    def __init__(self):
        self.__value = 0

    def reset(self):
        self.__value = 0

    def __call__(self):
        self.__value += 1
        return self.__value


class TimingTestCase(unittest.TestCase):
    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        action = ActionFromCallable(mock, name)
        return action, mock

    def setUp(self):
        patcher = unittest.mock.patch("datetime.datetime")
        self.datetime = patcher.start()
        self.datetime.now.side_effect = Counter()
        self.addCleanup(patcher.stop)

    def test_success(self):
        a, aMock = self.__create_mocked_action("a")

        report = execute(a)

        self.assertEqual(report.get_action_status(a).ready_time, 1)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertEqual(report.get_action_status(a).start_time, 2)
        self.assertEqual(report.get_action_status(a).success_time, 3)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_failure(self):
        a, aMock = self.__create_mocked_action("a")
        aMock.side_effect = Exception()

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(report.get_action_status(a).ready_time, 1)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertEqual(report.get_action_status(a).start_time, 2)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertEqual(report.get_action_status(a).failure_time, 3)

    def test_cancelation_before_ready(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        bMock.side_effect = Exception()
        a.add_dependency(b)

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(report.get_action_status(b).ready_time, 1)
        self.assertIsNone(report.get_action_status(b).cancel_time)
        self.assertEqual(report.get_action_status(b).start_time, 2)
        self.assertIsNone(report.get_action_status(b).success_time)
        self.assertEqual(report.get_action_status(b).failure_time, 3)

        self.assertIsNone(report.get_action_status(a).ready_time)
        self.assertEqual(report.get_action_status(a).cancel_time, 4)
        self.assertIsNone(report.get_action_status(a).start_time)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_cancelation_with_keep_going(self):
        for i in range(10):
            self.datetime.now.side_effect.reset()

            a0, a0Mock = self.__create_mocked_action("a0")
            a, aMock = self.__create_mocked_action("a")
            a0.add_dependency(a)
            b, bMock = self.__create_mocked_action("b")
            bMock.side_effect = Exception()
            a.add_dependency(b)
            DEPS = 10
            deps = []
            for i in range(DEPS):
                c, cMock = self.__create_mocked_action("c")
                a.add_dependency(c)
                deps.append(c)

            with self.assertRaises(CompoundException) as catcher:
                execute(a0, keep_going=True)
            report = catcher.exception.execution_report

            # a is not cancelled before all its dependencies are done
            self.assertGreater(report.get_action_status(a).cancel_time, 3 + 2 * DEPS)
            # a0 is cancelled at the same time as a
            self.assertEqual(report.get_action_status(a0).cancel_time, report.get_action_status(a).cancel_time)
