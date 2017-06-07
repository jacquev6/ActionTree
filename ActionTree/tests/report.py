# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

# import collections
# import datetime
# import functools
# import math
import unittest

# import matplotlib.backends.backend_agg
# import matplotlib.figure

# import ActionTree
from ActionTree.drawings import *


# MockAction = collections.namedtuple("MockAction", "label, dependencies, begin_time, end_time, status")

# successful = ActionTree.Action.Successful
# failed = ActionTree.Action.Failed
# canceled = ActionTree.Action.Canceled


class UtilitiesTestCase(unittest.TestCase):
    def test_nearest_before_first(self):
        self.assertEqual(nearest(2, [10, 20, 30]), 10)

    def test_nearest_after_last(self):
        self.assertEqual(nearest(35, [10, 20, 30]), 30)

    def test_nearest_in_the_middle(self):
        self.assertEqual(nearest(18, [10, 20, 30]), 20)
        self.assertEqual(nearest(22, [10, 20, 30]), 20)


# class ExecutionReportTestCase(unittest.TestCase):
#     def test_simple_attributes(self):
#         a = MockAction("a", [], 10.5, 11.5, successful)
#         b = MockAction("b", [], 10.7, 11.7, successful)
#         c = MockAction("c", [a, b], 11.8, 13.7, successful)

#         r = ExecutionReport(c)
#         self.assertEqual(r.root_action.label, "c")
#         self.assertEqual(len(r.actions), 3)
#         self.assertEqual(r.begin_time, 10.5)
#         self.assertEqual(r.end_time, 13.7)
#         self.assertAlmostEqual(r.duration, 3.2)

#     def test_ordinates_of_tree_dependencies(self):
#         a = MockAction(
#             "a",
#             [
#                 MockAction(
#                     "b",
#                     [
#                         MockAction("c", [], 0, 1, successful),
#                         MockAction("d", [], 0, 2, successful),
#                         MockAction("e", [], 0, 3, successful),
#                     ],
#                     4, 5,
#                     successful
#                 ),
#                 MockAction(
#                     "f",
#                     [
#                         MockAction("g", [], 1, 2, successful),
#                         MockAction("h", [], 1, 3, successful),
#                         MockAction("i", [], 1, 4, successful),
#                     ],
#                     4, 6,
#                     successful
#                 ),
#             ],
#             6, 7,
#             successful
#         )

#         r = ExecutionReport(a)
#         self.assertEqual(
#             [a.label for a in r.actions],
#             ["i", "h", "g", "f", "e", "d", "c", "b", "a"]
#         )

#     def test_ordinates_of_diamond_dependencies(self):
#         x = MockAction("x", [], 0, 1, successful)
#         a = MockAction(
#             "a",
#             [
#                 MockAction("b", [x], 1, 2, successful),
#                 MockAction("c", [x], 1, 3, successful),
#             ],
#             3, 4,
#             successful
#         )

#         r = ExecutionReport(a)
#         self.assertEqual(
#             [a.label for a in r.actions],
#             ["x", "c", "b", "a"]
#         )

#     def test_plot_on_mpl_axes(self):
#         dt = functools.partial(datetime.datetime, 2015, 05, 14, 18, 40)
#         ab, ae = dt(3, 750), dt(4, 750)
#         bb, be = dt(1, 500), dt(2, 500)
#         cb, ce = dt(1, 250), dt(3, 250)
#         a = MockAction(
#             "a",
#             [
#                 MockAction("b", [], bb, be, successful),
#                 MockAction("c", [], cb, ce, failed),
#             ],
#             ab, ae,
#             canceled
#         )
#         r = ExecutionReport(a)
#         ax = unittest.mock.Mock()

#         r.plot_on_mpl_axes(ax)

#         call = unittest.mock.call
#         self.assertEqual(
#             ax.mock_calls[:14],
#             [
#                 call.plot([dt(1, 250), dt(3, 250)], [3, 3], color="red", lw=4),
#                 call.annotate("c", textcoords="offset points", xy=(dt(1, 250), 3), xytext=(0, 3)),
#                 call.plot([dt(1, 500), dt(2, 500)], [2, 2], color="blue", lw=4),
#                 call.annotate("b", textcoords="offset points", xy=(dt(1, 500), 2), xytext=(0, 3)),
#                 call.plot([dt(3, 750), dt(4, 750)], [1, 1], color="gray", lw=4),
#                 call.annotate("a", textcoords="offset points", xy=(dt(3, 750), 1), xytext=(0, 3)),
#                 call.plot([dt(2, 500), dt(3, 750)], [2, 1], "k:", lw=1),
#                 call.plot([dt(3, 250), dt(3, 750)], [3, 1], "k:", lw=1),
#                 call.get_yaxis(),
#                 call.get_yaxis().set_ticklabels([]),
#                 call.set_ylim(0.5, 4),
#                 call.set_xlabel("Local time"),
#                 call.set_xlim(dt(1), dt(5)),
#                 call.xaxis_date(),
#             ]
#         )

#         self.assertEqual(ax.mock_calls[14][0], "xaxis.set_major_formatter")
#         self.assertEqual(ax.mock_calls[15][0], "xaxis.set_major_locator")

#         self.assertEqual(
#             ax.mock_calls[16:],
#             [
#                 call.twiny(),
#                 call.twiny().set_xlabel("Relative time"),
#                 call.twiny().set_xlim(dt(1), dt(5)),
#                 call.twiny().xaxis.set_ticks([dt(1, 250), dt(2, 250), dt(3, 250), dt(4, 250)]),
#                 call.twiny().xaxis.set_ticklabels([0, 1, 2, 3]),
#             ]
#         )
