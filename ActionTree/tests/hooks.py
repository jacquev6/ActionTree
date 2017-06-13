# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import datetime

from ActionTree import *
from . import *


class TestHooks(Hooks):
    def __init__(self):
        self.events = []

    def action_pending(self, time, action):
        assert isinstance(time, datetime.datetime)
        self.events.append(("pending", action.label))

    def action_ready(self, time, action):
        assert isinstance(time, datetime.datetime)
        self.events.append(("ready", action.label))

    def action_canceled(self, time, action):
        assert isinstance(time, datetime.datetime)
        self.events.append(("canceled", action.label))

    def action_started(self, time, action):
        assert isinstance(time, datetime.datetime)
        self.events.append(("started", action.label))

    def action_printed(self, time, action, text):
        assert isinstance(time, datetime.datetime)
        self.events.append(("printed", action.label, text))

    def action_successful(self, time, action, return_value):
        assert isinstance(time, datetime.datetime)
        self.events.append(("successful", action.label, return_value))

    def action_failed(self, time, action, exception):
        assert isinstance(time, datetime.datetime)
        self.events.append(("failed", action.label, str(exception)))


class ExecutionTestCase(ActionTreeTestCase):
    def test_successful_action(self):
        hooks = TestHooks()
        execute(self._action("a", return_value="return"), hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("successful", "a", "return"),
            ]
        )

    def test_failed_action(self):
        hooks = TestHooks()
        execute(self._action("a", exception=Exception("foo")), do_raise=False, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("failed", "a", "foo"),
            ]
        )

    def test_failed_dependency(self):
        hooks = TestHooks()
        a = self._action("a")
        b = self._action("b", exception=Exception("foo"))
        a.add_dependency(b)
        execute(a, do_raise=False, hooks=hooks)

        self.assertEqual(sorted(hooks.events[:2]), [("pending", "a"), ("pending", "b")])
        self.assertEqual(
            hooks.events[2:],
            [
                ("ready", "b"),
                ("started", "b"),
                ("failed", "b", "foo"),
                ("canceled", "a"),
            ]
        )

    def test_successful_action_print(self):
        hooks = TestHooks()
        execute(self._action("a", print_on_stdout="something"), hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("printed", "a", "something\n"),
                ("successful", "a", None),
            ]
        )

    def test_failed_action_print(self):
        hooks = TestHooks()
        execute(self._action("a", print_on_stdout="something", exception=Exception("foo")), do_raise=False, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("printed", "a", "something\n"),
                ("failed", "a", "foo"),
            ]
        )

    def test_print_several_times(self):
        hooks = TestHooks()
        a = self._action("a", print_on_stdout=[("something 1", 0.1), ("something 2", 0.1), ("something 3", 0.1)])
        execute(a, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("printed", "a", "something 1\n"),
                ("printed", "a", "something 2\n"),
                ("printed", "a", "something 3\n"),
                ("successful", "a", None),
            ]
        )

    def test_leaves_are_ready_at_once(self):
        hooks = TestHooks()
        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        execute(a, hooks=hooks)

        self.assertEqual(
            sorted(hooks.events[0:4]),
            [
                ("pending", "a"),
                ("pending", "b"),
                ("pending", "c"),
                ("pending", "d"),
            ]
        )
        self.assertEqual(
            sorted(hooks.events[4:7]),
            [
                ("ready", "b"),
                ("ready", "c"),
                ("ready", "d"),
            ]
        )
