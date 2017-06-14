# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

from ActionTree import *
from . import *


class UtilitiesTestCase(unittest.TestCase):
    def test_nearest_before_first(self):
        self.assertEqual(GanttChart._GanttChart__nearest(2, [10, 20, 30]), 10)

    def test_nearest_after_last(self):
        self.assertEqual(GanttChart._GanttChart__nearest(35, [10, 20, 30]), 30)

    def test_nearest_in_the_middle(self):
        self.assertEqual(GanttChart._GanttChart__nearest(18, [10, 20, 30]), 20)
        self.assertEqual(GanttChart._GanttChart__nearest(22, [10, 20, 30]), 20)


class GanttChartTestCase(ActionTreeTestCase):
    def test(self):
        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        c.add_dependency(a)
        c.add_dependency(b)

        chart = GanttChart(execute(c, cpu_cores=2))
        ax = unittest.mock.Mock()
        chart.plot_on_mpl_axes(ax)
