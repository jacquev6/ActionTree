# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock

from ActionTree import Action, TimedAction


class Timing(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self.mocks = MockMockMock.Engine()
        self.m = self.mocks.create("m")
        self.time = self.mocks.create("time")

        self.a = TimedAction(self.m.object, "timed")
        TimedAction.time = self.time.object

    def testExecution(self):
        self.time.expect().andReturn(1352032735.2)
        self.m.expect()
        self.time.expect().andReturn(1352032737.1)

        self.a.execute()
        self.assertEqual(self.a.beginTime, 1352032735.2)
        self.assertEqual(self.a.endTime, 1352032737.1)

    def testFailure(self):
        e = Exception()

        self.time.expect().andReturn(1352032735.2)
        self.m.expect().andRaise(e)
        self.time.expect().andReturn(1352032737.1)

        with self.assertRaises(Action.Exception) as cm:
            self.a.execute()
        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertIs(cm.exception.exceptions[0], e)

        self.assertEqual(self.a.beginTime, 1352032735.2)
        self.assertEqual(self.a.endTime, 1352032737.1)
