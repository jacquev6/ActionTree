# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

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
