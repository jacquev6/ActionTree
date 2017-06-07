# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import ActionFromCallable as Action, CompoundException, execute


class TimingTestCase(unittest.TestCase):
    def setUp(self):
        self.m = unittest.mock.Mock()
        self.a = Action(self.m, "timed")
        patcher = unittest.mock.patch("datetime.datetime")
        self.datetime = patcher.start()
        self.addCleanup(patcher.stop)

    def test_success(self):
        self.datetime.now.side_effect = [1352032735.2, 1352032737.1]

        report = execute(self.a)

        self.m.assert_called_once_with()
        self.assertEqual(self.datetime.mock_calls, [unittest.mock.call.now(), unittest.mock.call.now()])

        self.assertEqual(report.get_action_status(self.a).begin_time, 1352032735.2)
        self.assertEqual(report.get_action_status(self.a).end_time, 1352032737.1)

    def test_failure(self):
        self.datetime.now.side_effect = [1352032735.2, 1352032737.1]
        self.m.side_effect = Exception()

        with self.assertRaises(CompoundException) as catcher:
            execute(self.a)
        report = catcher.exception.execution_report

        self.m.assert_called_once_with()
        self.assertEqual(self.datetime.mock_calls, [unittest.mock.call.now(), unittest.mock.call.now()])

        self.assertEqual(report.get_action_status(self.a).begin_time, 1352032735.2)
        self.assertEqual(report.get_action_status(self.a).end_time, 1352032737.1)
