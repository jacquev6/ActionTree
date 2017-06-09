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

    # def test_exceptions_in_dependencies_without_keep_going(self):
    #     a = self._action("a")
    #     b = self._action("b", delay=5, exception=Exception())
    #     c = self._action("c", delay=5, exception=Exception())
    #     d = self._action("d", delay=5, exception=Exception())
    #     a.add_dependency(b)
    #     a.add_dependency(c)
    #     a.add_dependency(d)

    #     with self.assertRaises(CompoundException) as catcher:
    #         execute(a, jobs=1, keep_going=False)
    #     report = catcher.exception.execution_report

    #     failed = len(catcher.exception.exceptions)

    #     if failed == 1:
    #         self.assertEventsIn([
    #             ["b"],
    #             ["c"],
    #             ["d"],
    #         ])
    #     else:
    #         self.assertEqual(failed, 2)
    #         self.assertEventsIn([
    #             ["b", "c"],
    #             ["b", "d"],
    #             ["c", "b"],
    #             ["c", "d"],
    #             ["d", "b"],
    #             ["d", "c"],
    #         ])

    #     self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.Canceled)
    #     self.assertEqual(
    #         len([x for x in [b, c, d] if report.get_action_status(x).status ==
    #                ExecutionReport.ActionStatus.Canceled]),
    #         3 - failed
    #     )
    #     self.assertEqual(
    #         len([x for x in [b, c, d] if report.get_action_status(x).status == ExecutionReport.ActionStatus.Failed]),
    #         failed
    #     )
