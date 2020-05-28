# coding: utf8

# Copyright 2015-2018 Vincent Jacques <vincent@vincent-jacques.net>


from ActionTree import *
from . import *


class MultiThreadedExecutionTestCase(ActionTreeTestCase):
    def test_many_dependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a = self._action("a")
        barrier = self._barrier(3)
        b = self._action("b", barrier=barrier, end_event=True)
        c = self._action("c", barrier=barrier, end_event=True)
        d = self._action("d", barrier=barrier, end_event=True)
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        execute(a, cpu_cores=3)

        self.assertEventsEqual("bcd BCD a")

    # @todo Understand why this failed on Travis (https://travis-ci.org/jacquev6/ActionTree/jobs/464953921#L675)
    # def test_many_dependencies_with_default_cpu_cores(self):
    #     #     a
    #     #    /|\
    #     #   / | \
    #     #  b  c  d

    #     a = self._action("a")
    #     barrier = self._barrier(3)
    #     b = self._action("b", barrier=barrier, end_event=True)
    #     c = self._action("c", barrier=barrier, end_event=True)
    #     d = self._action("d", barrier=barrier, end_event=True)
    #     a.add_dependency(b)
    #     a.add_dependency(c)
    #     a.add_dependency(d)

    #     execute(a, cpu_cores=None)

    #     self.assertEventsEqual("bcd BCD a")

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
        b = self._action("b", end_event=True)
        c = self._action("c", end_event=True)
        d = self._action("d", end_event=True)
        e = self._action("e", end_event=True)
        f = self._action("f", end_event=True)
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        e.add_dependency(f)

        execute(a, cpu_cores=3)

        self.assertEventsEqual("f F e E d D c C b B a")

    def test_diamond_dependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a = self._action("a")
        barrier = self._barrier(2)
        b = self._action("b", barrier=barrier, end_event=True)
        c = self._action("c", barrier=barrier, end_event=True)
        d = self._action("d", end_event=True)
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

        execute(a, cpu_cores=3)

        self.assertEventsEqual("d D bc BC a")

    def test_half_diamond_dependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a = self._action("a")
        b = self._action("b", end_event=True)
        d = self._action("d", end_event=True)
        a.add_dependency(b)
        a.add_dependency(d)
        b.add_dependency(d)

        execute(a, cpu_cores=3)

        self.assertEventsEqual("d D b B a")

    def test_two_deep_branches(self):
        #     a
        #    / \
        #   b   c
        #   |   |
        #   d   e

        a = self._action("a")
        barrier1 = self._barrier(2)
        b = self._action("b", barrier=barrier1, end_event=True)
        c = self._action("c", barrier=barrier1, end_event=True)
        barrier2 = self._barrier(2)
        d = self._action("d", barrier=barrier2, end_event=True)
        e = self._action("e", barrier=barrier2, end_event=True)
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(e)

        execute(a, cpu_cores=3)

        self.assertEventsEqual("de DEbc BC a")
