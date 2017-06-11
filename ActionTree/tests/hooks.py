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

    # def action_started(self, action):
    #     self.events.append(("started", action.label))

    def action_successful(self, action):
        self.events.append(("successful", action.label))

    def action_failed(self, action):
        self.events.append(("failed", action.label))

    def action_canceled(self, action):
        self.events.append(("canceled", action.label))


class ExecutionTestCase(ActionTreeTestCase):
    def test_one_successful_action(self):
        hooks = TestHooks()
        execute(self._action("a"), hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                # ("started", "a"),
                ("successful", "a"),
            ]
        )

    def test_one_failed_action(self):
        hooks = TestHooks()
        execute(self._action("a", exception=Exception()), do_raise=False, hooks=hooks)

        self.assertEqual(
            hooks.events,
            [
                ("pending", "a"),
                ("ready", "a"),
                # ("started", "a"),
                ("failed", "a"),
            ]
        )

    def test_one_failed_dependency(self):
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
                # ("started", "b"),
                ("failed", "b"),
                ("canceled", "a"),
            ]
        )
