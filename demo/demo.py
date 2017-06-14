#!/usr/bin/env python3

import datetime
import sys
import time

from ActionTree import Action, execute, Hooks


UNKNOWN = (0, "unwknown since")
PENDING = (1, "pending since")
READY = (2, "ready since")
STARTED = (3, "running since")
SUCCESSFUL = (4, "succeeded at")
FAILED = (5, "FAILED at")
CANCELED = (6, "canceled at")


class DemoHooks(Hooks):
    class ActionStatus:
        num_lines = {
            UNKNOWN: 0,
            PENDING: 0,
            READY: 0,
            STARTED: 5,
            SUCCESSFUL: 2,
            FAILED: 10,
            CANCELED: 0,
        }

        def __init__(self, label, time, status):
            self.label = label
            self.status = status
            self.time = time
            self.lines = []

        def set(self, time, status):
            self.time = time
            self.status = status

        def display(self):
            num_lines = self.num_lines[self.status]
            title = "\"{}\" ({} t={:.2f}s)".format(self.label, self.status[1], self.time.total_seconds())
            print()
            print(title)
            print("-" * len(title))
            if num_lines > 1:
                if len(self.lines) > num_lines:
                    print("[... {} lines not displayed ...]".format(len(self.lines) - num_lines))
                    lines_to_display = self.lines[1 - num_lines:]
                    padding = 0
                else:
                    lines_to_display = self.lines
                    padding = num_lines - len(self.lines)
                for line in lines_to_display:
                    print(line)
                for i in range(padding):
                    print()

    def __init__(self, action):
        self.start_time = datetime.datetime.now()
        actions = action.get_possible_execution_order()
        self.action_statuses = [self.ActionStatus(a.label, datetime.timedelta(), UNKNOWN) for a in actions]
        self.action_indexes = {action: i for (i, action) in enumerate(actions)}
        self.display()

    def display(self):
        print("\x1b[2J\x1b[H")
        title = "ActionTree demo (t={:.2f}s)".format((datetime.datetime.now() - self.start_time).total_seconds())
        print(title)
        print("=" * len(title))
        for action_status in self.action_statuses:
            action_status.display()

    def set(self, action, time, status):
        self.action_statuses[self.action_indexes[action]].set(time - self.start_time, status)
        self.display()

    def action_pending(self, time, action):
        self.set(action, time, PENDING)

    def action_ready(self, time, action):
        self.set(action, time, READY)

    def action_canceled(self, time, action):
        self.set(action, time, CANCELED)

    def action_started(self, time, action):
        self.set(action, time, STARTED)

    def action_printed(self, time, action, text):
        self.action_statuses[self.action_indexes[action]].lines += ["> {}".format(line.rstrip()) for line in text.splitlines()]
        self.display()

    def action_successful(self, time, action, return_value):
        self.set(action, time, SUCCESSFUL)

    def action_failed(self, time, action, exception):
        self.action_statuses[self.action_indexes[action]].lines += ["Exception: {}".format(exception)]
        self.set(action, time, FAILED)


class DemoAction(Action):
    def __init__(self, label, interval, iterations, exception=None):
        super(DemoAction, self).__init__("action {}".format(label))
        self.interval = interval
        self.iterations = iterations
        self.exception = exception

    def do_execute(self, dependency_statuses):
        print(self.label, "iteration 0 /", self.iterations)
        for i in range(self.iterations):
            time.sleep(self.interval)
            print(self.label, "iteration", (i + 1), "/", self.iterations)
        if self.exception:
            print(self.label, "failing")
            raise self.exception


a = DemoAction("a", 1., 5)
a.add_dependency(DemoAction("a1", 0.9, 7))
a.add_dependency(DemoAction("a2", 0.5, 12))
a.add_dependency(DemoAction("a3", 0.8, 10))

b = DemoAction("b", 1., 5)
b.add_dependency(DemoAction("b1", 0.5, 14, exception=Exception()))
b.add_dependency(DemoAction("b2", 0.3, 25))
b.add_dependency(DemoAction("b3", 1.7, 5))

z = DemoAction("z", 1., 5)
z.add_dependency(a)
z.add_dependency(b)

execute(z, jobs=4, hooks=DemoHooks(z), do_raise=False, keep_going=True)
