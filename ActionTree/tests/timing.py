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
        self.assertEqual(report.get_action_status(a).ready_time, report.get_action_status(a).pending_time)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertEqual(report.get_action_status(a).start_time, report.get_action_status(a).ready_time)
        self.assertGreater(report.get_action_status(a).success_time, report.get_action_status(a).start_time)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_failure(self):
        a = self._action("a", exception=Exception())

        report = execute(a, do_raise=False)

        self.assertIsInstance(report.get_action_status(a).pending_time, datetime.datetime)
        self.assertEqual(report.get_action_status(a).ready_time, report.get_action_status(a).pending_time)
        self.assertIsNone(report.get_action_status(a).cancel_time)
        self.assertEqual(report.get_action_status(a).start_time, report.get_action_status(a).ready_time)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertGreater(report.get_action_status(a).failure_time, report.get_action_status(a).start_time)

    def test_cancelation_before_ready(self):
        a = self._action("a")
        b = self._action("b", exception=Exception())
        a.add_dependency(b)

        report = execute(a, do_raise=False)

        self.assertIsInstance(report.get_action_status(b).pending_time, datetime.datetime)
        self.assertEqual(report.get_action_status(b).ready_time, report.get_action_status(b).pending_time)
        self.assertIsNone(report.get_action_status(b).cancel_time)
        self.assertEqual(report.get_action_status(b).start_time, report.get_action_status(b).ready_time)
        self.assertIsNone(report.get_action_status(b).success_time)
        self.assertGreater(report.get_action_status(b).failure_time, report.get_action_status(b).start_time)

        self.assertIsInstance(report.get_action_status(a).pending_time, datetime.datetime)
        self.assertIsNone(report.get_action_status(a).ready_time)
        self.assertEqual(report.get_action_status(a).cancel_time, report.get_action_status(b).failure_time)
        self.assertIsNone(report.get_action_status(a).start_time)
        self.assertIsNone(report.get_action_status(a).success_time)
        self.assertIsNone(report.get_action_status(a).failure_time)

    def test_cancelation_with_keep_going(self):
        a = self._action("a")
        b = self._action("b")
        a.add_dependency(b)
        c = self._action("c", exception=Exception())
        b.add_dependency(c)

        report = execute(a, keep_going=True, do_raise=False)

        self.assertEqual(report.get_action_status(b).cancel_time, report.get_action_status(c).failure_time)
        self.assertEqual(report.get_action_status(a).cancel_time, report.get_action_status(b).cancel_time)

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

    def test_many_dependencies_with_unlimited_cpu_cores(self):
        MANY = 20
        a = self._action("a")
        deps = [self._action(i) for i in range(MANY)]
        for dep in deps:
            a.add_dependency(dep)

        report = execute(a, cpu_cores=UNLIMITED)
        for dep in deps[1:]:
            self.assertEqual(report.get_action_status(dep).start_time, report.get_action_status(deps[0]).start_time)

    def test_many_dependencies_with_one_cpu_cores(self):
        MANY = 20
        a = self._action("a")
        deps = [self._action(i) for i in range(MANY)]
        for dep in deps:
            a.add_dependency(dep)

        report = execute(a, cpu_cores=1)

        # No two actions have started at the same time
        start_times = set(report.get_action_status(dep).start_time for dep in deps)
        self.assertEqual(len(start_times), MANY)

    def test_many_dependencies_with_limited_cpu_cores(self):
        MANY = 20
        a = self._action("a")
        deps = [self._action(i) for i in range(MANY)]
        for dep in deps:
            a.add_dependency(dep)

        report = execute(a, cpu_cores=3)

        # Only the first three actions have started at the same time
        start_times = set(report.get_action_status(dep).start_time for dep in deps)
        self.assertEqual(len(start_times), MANY - 2)

    def test_scarce_resource_with_many_cpu_cores(self):
        r = Resource(1)
        a = self._action("a")
        b = self._action("b")
        b.require_resource(r, 1)
        c = self._action("c")
        c.require_resource(r, 1)
        a.add_dependency(b)
        a.add_dependency(c)

        report = execute(a, cpu_cores=6)

        # @todo Start next action at the same timestamp
        self.assertTrue(
            report.get_action_status(b).start_time > report.get_action_status(c).success_time or
            report.get_action_status(c).start_time > report.get_action_status(b).success_time
        )

    def test_abundant_resource_with_many_cpu_cores(self):
        r = Resource(2)
        a = self._action("a")
        b = self._action("b")
        b.require_resource(r, 1)
        c = self._action("c")
        c.require_resource(r, 1)
        a.add_dependency(b)
        a.add_dependency(c)

        report = execute(a, cpu_cores=6)

        self.assertEqual(report.get_action_status(c).ready_time, report.get_action_status(b).ready_time)
        self.assertEqual(report.get_action_status(c).start_time, report.get_action_status(b).start_time)
