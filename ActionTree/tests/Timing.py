# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

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
