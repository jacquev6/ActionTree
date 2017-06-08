# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

# import datetime
# import functools
import unittest

from ActionTree import *


class UtilitiesTestCase(unittest.TestCase):
    def test_nearest_before_first(self):
        self.assertEqual(GanttChart._GanttChart__nearest(2, [10, 20, 30]), 10)

    def test_nearest_after_last(self):
        self.assertEqual(GanttChart._GanttChart__nearest(35, [10, 20, 30]), 30)

    def test_nearest_in_the_middle(self):
        self.assertEqual(GanttChart._GanttChart__nearest(18, [10, 20, 30]), 20)
        self.assertEqual(GanttChart._GanttChart__nearest(22, [10, 20, 30]), 20)


class Counter:
    def __init__(self):
        self.__value = datetime.datetime(2017, 6, 8, 13, 47, 12)

    def __call__(self):
        self.__value += datetime.timedelta(seconds=2)
        return self.__value


class GanttChartTestCase(unittest.TestCase):
    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        action = ActionFromCallable(mock, name)
        return action, mock

    def setUp(self):
        counter = Counter()
        patcher = unittest.mock.patch("datetime.datetime")
        self.datetime = patcher.start()
        self.datetime.now.side_effect = counter
        self.addCleanup(patcher.stop)

    def test(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        c.add_dependency(a)
        c.add_dependency(b)

        chart = GanttChart(execute(c, jobs=2))
        ax = unittest.mock.Mock()
        chart.plot_on_mpl_axes(ax)
        # @todo Assert something about calls to ax
