# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

from ActionTree import *
from . import *


class ExecutionTestCase(ActionTreeTestCase):
    def test_simple_execution(self):
        a = self._action("a", return_value=42)

        report = execute(a)

        self.assertTrue(report.is_success)
        self.assertEqual(report.get_action_status(a).status, ExecutionReport.ActionStatus.SUCCESSFUL)
        self.assertEqual(report.get_action_status(a).return_value, 42)

    def test_many_dependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        execute(a)

        self.assertEventsEqual("bcd a")

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

        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        e = self._action("e")
        f = self._action("f")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        e.add_dependency(f)

        execute(a)

        self.assertEventsEqual("f e d c b a")

    def test_diamond_dependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        execute(a)

        self.assertEventsEqual("d bc a")

    def test_half_diamond_dependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a = self._action("a")
        b = self._action("b")
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(d)
        b.add_dependency(d)

        execute(a)

        self.assertEventsEqual("d b a")

    def test_two_deep_branches(self):
        #     a
        #    / \
        #   b   c
        #   |   |
        #   d   e

        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        e = self._action("e")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(e)

        execute(a)

        self.assertEventsIn([
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
        ])
