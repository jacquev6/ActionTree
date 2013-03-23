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

from ActionTree import Action


class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__mockEngine = MockMockMock.Engine()
        self.__mocks = dict()
        self.__actions = dict()
        for name in "abcdef":
            self.__addMock(name)

    def __addMock(self, name):
        m = self.__mockEngine.create(name)
        a = Action(self.callableFromMock(m.object), name)
        self.__mocks[name] = m
        self.__actions[name] = a

    def callableFromMock(self, m):
        return m

    def tearDown(self):
        self.__mockEngine.tearDown()

    def addDependency(self, a, b):
        self.__actions[a].addDependency(self.__actions[b])

    def getMock(self, name):
        return self.__mocks[name]

    def getAction(self, name):
        return self.__actions[name]

    @property
    def unordered(self):
        return self.__mockEngine.unordered

    @property
    def optional(self):
        return self.__mockEngine.optional
