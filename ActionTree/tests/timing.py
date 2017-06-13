# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *
from . import *


class TimingTestCase(ActionTreeTestCase):
    def test_success(self):
        a = self._action("a")

        report = execute(a)

        self.assertIsInstance(report.get_action_status(a).pending_time, datetime.datetime)
        self.assertGreater(report.get_action_status(a).ready_time, report.get_action_status(a).pending_time)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertGreater(report.get_action_status(a).start_time, report.get_action_status(a).ready_time)
        self.assertGreater(report.get_action_status(a).success_time, report.get_action_status(a).start_time)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_failure(self):
        a = self._action("a", exception=Exception())

        report = execute(a, do_raise=False)

        self.assertIsInstance(report.get_action_status(a).ready_time, datetime.datetime)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertGreater(report.get_action_status(a).start_time, report.get_action_status(a).ready_time)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertGreater(report.get_action_status(a).failure_time, report.get_action_status(a).start_time)

    def test_cancelation_before_ready(self):
        a = self._action("a")
        b = self._action("b", exception=Exception())
        a.add_dependency(b)

        report = execute(a, do_raise=False)

        self.assertIsInstance(report.get_action_status(b).ready_time, datetime.datetime)
        self.assertIsNone(report.get_action_status(b).cancel_time)
        self.assertGreater(report.get_action_status(b).start_time, report.get_action_status(b).ready_time)
        self.assertIsNone(report.get_action_status(b).success_time)
        self.assertGreater(report.get_action_status(b).failure_time, report.get_action_status(b).start_time)

        self.assertIsNone(report.get_action_status(a).ready_time)
        self.assertGreater(report.get_action_status(a).cancel_time, report.get_action_status(b).failure_time)
        self.assertIsNone(report.get_action_status(a).start_time)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_cancelation_with_keep_going(self):
        for i in range(10):
            a0 = self._action("a0")
            a = self._action("a")
            a0.add_dependency(a)
            b = self._action("b", exception=Exception())
            a.add_dependency(b)
            DEPS = 10
            deps = []
            for i in range(DEPS):
                c = self._action("c")
                a.add_dependency(c)
                deps.append(c)

            report = execute(a0, keep_going=True, do_raise=False)

            # a is not canceled before all its dependencies are done
            self.assertGreater(report.get_action_status(a).cancel_time, report.get_action_status(b).failure_time)
            for dep in deps:
                self.assertGreater(report.get_action_status(a).cancel_time, report.get_action_status(dep).success_time)
            # a0 is canceled at the same time as a
            self.assertEqual(report.get_action_status(a0).cancel_time, report.get_action_status(a).cancel_time)

    def test_leaves_have_same_ready_time(self):
        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        report = execute(a)

        self.assertEqual(report.get_action_status(c).ready_time, report.get_action_status(b).ready_time)
        self.assertEqual(report.get_action_status(d).ready_time, report.get_action_status(b).ready_time)
