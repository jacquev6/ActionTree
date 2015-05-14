# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import collections
import datetime
import math
import unittest

import matplotlib.backends.backend_agg
import matplotlib.figure

import ActionTree
from ActionTree.drawings import *


MockAction = collections.namedtuple("MockAction", "label, dependencies, begin_time, end_time, status")

successful = ActionTree.Action.Successful
failed = ActionTree.Action.Failed
canceled = ActionTree.Action.Canceled


class ExecutionReportTestCase(unittest.TestCase):
    def test_simple_attributes(self):
        a = MockAction("a", [], 10.5, 11.5, successful)
        b = MockAction("b", [], 10.7, 11.7, successful)
        c = MockAction("c", [a, b], 11.8, 13.7, successful)

        r = ExecutionReport(c)
        self.assertIs(r.root_action, c)
        self.assertEqual(len(r.actions), 3)
        self.assertEqual(r.begin_time, 10.5)
        self.assertEqual(r.end_time, 13.7)
        self.assertAlmostEqual(r.duration, 3.2)

    def test_ordinates_of_tree_dependencies(self):
        a01 = MockAction("a01", [], 0, 1, successful)
        a02 = MockAction("a02", [], 0, 2, successful)
        a03 = MockAction("a03", [], 0, 3, successful)
        b45 = MockAction("b45", [a01, a02, a03], 4, 5, successful)
        a12 = MockAction("a12", [], 1, 2, successful)
        a13 = MockAction("a13", [], 1, 3, successful)
        a14 = MockAction("a14", [], 1, 4, successful)
        b46 = MockAction("b46", [a12, a13, a14], 4, 6, successful)
        c = MockAction("c", [b45, b46], 6, 7, successful)

        r = ExecutionReport(c)
        self.assertEqual(
            [a.label for a in r.actions],
            ["a14", "a13", "a12", "b46", "a03", "a02", "a01", "b45", "c"]
        )


class ExecutionReportVisualTestCase(unittest.TestCase):
    now = datetime.datetime.now()

    def make_action(self, label, dependencies, begin_time, end_time, status):
        return MockAction(label, dependencies, self.now + datetime.timedelta(seconds=begin_time), self.now + datetime.timedelta(seconds=end_time), status)

    def make_actions(self):
        # Single
        yield self.make_action("a", [], 0, 1, successful)

        # Tree
        yield self.make_action(
            "a",
            [
                self.make_action(
                    "b",
                    [
                        self.make_action("c", [], 0, 1, successful),
                        self.make_action("d", [], 0, 2, successful),
                        self.make_action("e", [], 0, 3, successful),
                    ],
                    4, 5,
                    successful
                ),
                self.make_action(
                    "f",
                    [
                        self.make_action("g", [], 1, 2, successful),
                        self.make_action("h", [], 1, 3, successful),
                        self.make_action("i", [], 1, 4, successful),
                    ],
                    4, 6,
                    successful
                ),
            ],
            6, 7,
            successful
        )

        # Diamond
        x = self.make_action("x", [], 0, 1, successful)
        yield self.make_action(
            "a",
            [
                self.make_action("b", [x, self.make_action("y", [], 0, 2, successful)], 2, 3, successful),
                self.make_action("c", [x], 1, 4, successful),
            ],
            4, 5,
            successful
        )

        # Triamond?
        x = self.make_action("x", [], 0, 1, successful)
        y = self.make_action("y", [], 0, 2, successful)
        yield self.make_action(
            "a",
            [
                self.make_action("b", [x, y], 2, 3, successful),
                self.make_action("c", [x], 1, 4, successful),
                self.make_action("d", [x, y], 2, 5, successful),
            ],
            5, 6,
            successful
        )

    def test(self):
        figure = matplotlib.figure.Figure((16, 12))

        roots = list(self.make_actions())
        s = int(math.ceil(math.sqrt(len(roots))))
        for i, a in enumerate(roots):
            plot_report(a, figure.add_subplot(s, s, i + 1))

        figure.tight_layout()
        canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(figure)
        canvas.print_figure("execution_report_visual_test_case.png")
