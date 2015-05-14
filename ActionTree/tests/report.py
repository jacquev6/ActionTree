# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import collections
import datetime
import functools
import math
import unittest

import matplotlib.backends.backend_agg
import matplotlib.figure

import ActionTree
from ActionTree.drawings import *
from . import TestCaseWithMocks


MockAction = collections.namedtuple("MockAction", "label, dependencies, begin_time, end_time, status")

successful = ActionTree.Action.Successful
failed = ActionTree.Action.Failed
canceled = ActionTree.Action.Canceled


class UtilitiesTestCase(unittest.TestCase):
    def test_nearest_before_first(self):
        self.assertEqual(nearest(2, [10, 20, 30]), 10)

    def test_nearest_after_last(self):
        self.assertEqual(nearest(35, [10, 20, 30]), 30)

    def test_nearest_in_the_middle(self):
        self.assertEqual(nearest(18, [10, 20, 30]), 20)
        self.assertEqual(nearest(22, [10, 20, 30]), 20)


class ExecutionReportTestCase(TestCaseWithMocks):
    def test_simple_attributes(self):
        a = MockAction("a", [], 10.5, 11.5, successful)
        b = MockAction("b", [], 10.7, 11.7, successful)
        c = MockAction("c", [a, b], 11.8, 13.7, successful)

        r = ExecutionReport(c)
        self.assertEqual(r.root_action.label, "c")
        self.assertEqual(len(r.actions), 3)
        self.assertEqual(r.begin_time, 10.5)
        self.assertEqual(r.end_time, 13.7)
        self.assertAlmostEqual(r.duration, 3.2)

    def test_ordinates_of_tree_dependencies(self):
        a = MockAction(
            "a",
            [
                MockAction(
                    "b",
                    [
                        MockAction("c", [], 0, 1, successful),
                        MockAction("d", [], 0, 2, successful),
                        MockAction("e", [], 0, 3, successful),
                    ],
                    4, 5,
                    successful
                ),
                MockAction(
                    "f",
                    [
                        MockAction("g", [], 1, 2, successful),
                        MockAction("h", [], 1, 3, successful),
                        MockAction("i", [], 1, 4, successful),
                    ],
                    4, 6,
                    successful
                ),
            ],
            6, 7,
            successful
        )

        r = ExecutionReport(a)
        self.assertEqual(
            [a.label for a in r.actions],
            ["i", "h", "g", "f", "e", "d", "c", "b", "a"]
        )

    def test_ordinates_of_diamond_dependencies(self):
        x = MockAction("x", [], 0, 1, successful)
        a = MockAction(
            "a",
            [
                MockAction("b", [x], 1, 2, successful),
                MockAction("c", [x], 1, 3, successful),
            ],
            3, 4,
            successful
        )

        r = ExecutionReport(a)
        self.assertEqual(
            [a.label for a in r.actions],
            ["x", "c", "b", "a"]
        )

    def test_plot_on_mpl_axes(self):
        dt = functools.partial(datetime.datetime, 2015, 05, 14, 18, 40)
        ab, ae = dt(3, 750), dt(4, 750)
        bb, be = dt(1, 500), dt(2, 500)
        cb, ce = dt(1, 250), dt(3, 250)
        a = MockAction(
            "a",
            [
                MockAction("b", [], bb, be, successful),
                MockAction("c", [], cb, ce, failed),
            ],
            ab, ae,
            canceled
        )
        r = ExecutionReport(a)
        ax = self.mocks.create("ax")

        ax.expect.plot([cb, ce], [3, 3], color="red", lw=4)
        ax.expect.annotate("c", xy=(cb, 3), xytext=(0, 3), textcoords="offset points")
        ax.expect.plot([bb, be], [2, 2], color="blue", lw=4)
        ax.expect.annotate("b", xy=(bb, 2), xytext=(0, 3), textcoords="offset points")
        ax.expect.plot([ab, ae], [1, 1], color="gray", lw=4)
        ax.expect.annotate("a", xy=(ab, 1), xytext=(0, 3), textcoords="offset points")
        ax.expect.plot([be, ab], [2, 1], "k:", lw=1)
        ax.expect.plot([ce, ab], [3, 1], "k:", lw=1)

        yaxis = self.mocks.create("yaxis")
        ax.expect.get_yaxis().andReturn(yaxis.object)
        yaxis.expect.set_ticklabels([])
        ax.expect.set_ylim(0.5, 4)

        ax.expect.set_xlabel("Local time")
        ax.expect.set_xlim(dt(1), dt(5))
        ax.expect.xaxis_date()
        xaxis = self.mocks.create("xaxis")
        ax.expect.xaxis.andReturn(xaxis.object)
        xaxis.expect.set_major_formatter.withArguments(lambda args, kwds: True)
        ax.expect.xaxis.andReturn(xaxis.object)
        xaxis.expect.set_major_locator.withArguments(lambda args, kwds: True)

        ax2 = self.mocks.create("ax2")
        ax.expect.twiny().andReturn(ax2.object)
        ax2.expect.set_xlabel("Relative time")
        ax2.expect.set_xlim(dt(1), dt(5))
        ax2.expect.xaxis.andReturn(xaxis.object)
        xaxis.expect.set_ticks([dt(1, 250), dt(2, 250), dt(3, 250), dt(4, 250)])
        ax2.expect.xaxis.andReturn(xaxis.object)
        xaxis.expect.set_ticklabels([0, 1, 2, 3])

        r.plot_on_mpl_axes(ax.object)
