# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

import MockMockMock

from ActionTree import Action, CompoundException


class Timing(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self.mocks = MockMockMock.Engine()
        self.m = self.mocks.create("m")
        self.time = self.mocks.create("time")

        self.a = Action(self.m.object, "timed")
        self.oldTime = Action._time
        Action._time = self.time.object

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Action._time = self.oldTime

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

        self.assertRaises(CompoundException, self.a.execute)

        self.assertEqual(self.a.beginTime, 1352032735.2)
        self.assertEqual(self.a.endTime, 1352032737.1)
