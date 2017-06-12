# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

from ActionTree import *
from . import *


class TestHooks(Hooks):
    def __init__(self):
        self.events = []

    def action_pending(self, action):
        self.events.append(("pending", action.label))

    def action_ready(self, action):
        self.events.append(("ready", action.label))

    def action_started(self, action):
        self.events.append(("started", action.label))

    def action_printed(self, action, text):
        self.events.append(("printed", action.label, text))

    def action_successful(self, action):
        self.events.append(("successful", action.label))

    def action_failed(self, action):
        self.events.append(("failed", action.label))

    def action_canceled(self, action):
        self.events.append(("canceled", action.label))


class ExecutionTestCase(ActionTreeTestCase):
    def test_successful_action(self):
        hooks = TestHooks()
        execute(self._action("a"), hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("successful", "a"),
            ]
        )

    def test_failed_action(self):
        hooks = TestHooks()
        execute(self._action("a", exception=Exception()), do_raise=False, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("failed", "a"),
            ]
        )

    def test_failed_dependency(self):
        hooks = TestHooks()
        a = self._action("a")
        b = self._action("b", exception=Exception())
        a.add_dependency(b)
        execute(a, do_raise=False, hooks=hooks)

        self.assertEqual(sorted(hooks.events[:2]), [("pending", "a"), ("pending", "b")])
        self.assertEqual(
            hooks.events[2:],
            [
                ("ready", "b"),
                ("started", "b"),
                ("failed", "b"),
                ("canceled", "a"),
            ]
        )

    def test_successful_action_print(self):
        hooks = TestHooks()
        execute(self._action("a", print_on_stdout="something\nsomething else"), hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("printed", "a", b"something\nsomething else\n"),
                ("successful", "a"),
            ]
        )

    def test_failed_action_print(self):
        hooks = TestHooks()
        execute(self._action("a", print_on_stdout="something", exception=Exception()), do_raise=False, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                ("started", "a"),
                ("printed", "a", b"something\n"),
                ("failed", "a"),
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
                ("printed", "a", b"something 1\n"),
                ("printed", "a", b"something 2\n"),
                ("printed", "a", b"something 3\n"),
                ("successful", "a"),
            ]
        )
