# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

from ActionTree import *
from . import *


class ExceptionsHandlingTestCase(ActionTreeTestCase):
    def test_simple_failure(self):
        a = self._action("a", exception=Exception("foobar"))

        with self.assertRaises(CompoundException) as catcher:
            execute(a, jobs=1)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Failed)

    def test_simple_failure_without_raise(self):
        a = self._action("a", exception=Exception("foobar"))

        report = execute(a, jobs=1, do_raise=False)

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Failed)
        self.assertEqual(report.get_action_status(a).exception.args, ("foobar",))

    def test_exception_in_dependency(self):
        a = self._action("a")
        b = self._action("b", exception=Exception("foobar"))
        a.add_dependency(b)

        with self.assertRaises(CompoundException) as catcher:
            execute(a, jobs=1)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
        self.assertEqual(report.get_action_status(b).status, ExecutionReport.ActionStatus.Failed)

    def test_exceptions_in_dependencies_with_keep_going(self):
        a = self._action("a")
        b = self._action("b", exception=Exception("eb"))
        c = self._action("c", exception=Exception("ec"))
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        with self.assertRaises(CompoundException) as catcher:
            execute(a, jobs=1, keep_going=True)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 2)
        self.assertEqual(sorted(ex.args for ex in catcher.exception.exceptions), [("eb",), ("ec",)])

        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
        self.assertEqual(report.get_action_status(b).status, ExecutionReport.ActionStatus.Failed)
        self.assertEqual(report.get_action_status(c).status, ExecutionReport.ActionStatus.Failed)
        self.assertEqual(report.get_action_status(d).status, ExecutionReport.ActionStatus.Successful)

    def test_exceptions_in_long_branch_dependencies_with_keep_going(self):
        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        e = self._action("e", exception=Exception("foobar"))
        f = self._action("f")
        g = self._action("g")
        a.add_dependency(b)
        b.add_dependency(c)
        a.add_dependency(d)
        d.add_dependency(e)
        a.add_dependency(f)
        f.add_dependency(g)

        with self.assertRaises(CompoundException) as catcher:
            execute(a, jobs=1, keep_going=True)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
        self.assertEqual(report.get_action_status(b).status, ExecutionReport.ActionStatus.Successful)
        self.assertEqual(report.get_action_status(c).status, ExecutionReport.ActionStatus.Successful)
        self.assertEqual(report.get_action_status(d).status, ExecutionReport.ActionStatus.Canceled)
        self.assertEqual(report.get_action_status(e).status, ExecutionReport.ActionStatus.Failed)
        self.assertEqual(report.get_action_status(f).status, ExecutionReport.ActionStatus.Successful)
        self.assertEqual(report.get_action_status(g).status, ExecutionReport.ActionStatus.Successful)

    def test_exceptions_in_dependencies_without_keep_going(self):
        some_dependency_was_submitted_then_canceled_at_least_once = False
        for i in range(10):
            a = self._action("a")
            d0 = self._action("0", exception=Exception())
            a.add_dependency(d0)
            deps = [self._action(str(i)) for i in range(10)]
            for dep in deps:
                a.add_dependency(dep)

            report = execute(a, jobs=1, keep_going=False, do_raise=False)

            self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
            self.assertEqual(report.get_action_status(d0).status, ExecutionReport.ActionStatus.Failed)

            some_dependency_was_submitted_then_canceled_this_time = any(
                report.get_action_status(dep).status == ExecutionReport.ActionStatus.Canceled
                for dep in deps
            )
            some_dependency_was_submitted_then_canceled_at_least_once |= (
                some_dependency_was_submitted_then_canceled_this_time
            )
        self.assertTrue(some_dependency_was_submitted_then_canceled_at_least_once)
