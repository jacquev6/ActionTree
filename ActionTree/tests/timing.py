# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from ActionTree import Action, CompoundException
from . import TestCaseWithMocks


class TimingTestCase(TestCaseWithMocks):
    def setUp(self):
        super(TimingTestCase, self).setUp()
        self.m = self.mocks.create("m")
        self.time = self.mocks.replace("Action._time")
        self.a = Action(self.m.object, "timed")

    def test_before_execution(self):
        self.assertIsNone(self.a.begin_time)
        self.assertIsNone(self.a.end_time)

    def test_success(self):
        self.time.expect().andReturn(1352032735.2)
        self.m.expect()
        self.time.expect().andReturn(1352032737.1)

        self.a.execute()
        self.assertEqual(self.a.begin_time, 1352032735.2)
        self.assertEqual(self.a.end_time, 1352032737.1)

    def test_failure(self):
        e = Exception()

        self.time.expect().andReturn(1352032735.2)
        self.m.expect().andRaise(e)
        self.time.expect().andReturn(1352032737.1)

        self.assertRaises(CompoundException, self.a.execute)

        self.assertEqual(self.a.begin_time, 1352032735.2)
        self.assertEqual(self.a.end_time, 1352032737.1)
