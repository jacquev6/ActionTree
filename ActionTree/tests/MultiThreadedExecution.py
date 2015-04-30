# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import threading
import time
import unittest
import MockMockMock

from ActionTree import Action


class ExecuteMock:
    def __init__(self, mock):
        self.__mock = mock
        self.__lock = threading.Lock()

    def __call__(self):
        with self.__lock:
            self.__mock.begin()
        time.sleep(0.1)
        with self.__lock:
            self.__mock.end()


class MultiThreadedExecution(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __createMockedAction(self, name):
        mock = self.mocks.create(name + "Mock")
        action = Action(ExecuteMock(mock.object), name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def testManyDependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(c)
        a.addDependency(d)

        with self.mocks.unordered:
            bMock.expect.begin()
            cMock.expect.begin()
            dMock.expect.begin()
        with self.mocks.unordered:
            bMock.expect.end()
            cMock.expect.end()
            dMock.expect.end()
        aMock.expect.begin()
        aMock.expect.end()

        a.execute(jobs=-1)

    def testDeepDependencies(self):
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

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        e, eMock = self.__createMockedAction("e")
        f, fMock = self.__createMockedAction("f")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)
        d.addDependency(e)
        e.addDependency(f)

        fMock.expect.begin()
        fMock.expect.end()
        eMock.expect.begin()
        eMock.expect.end()
        dMock.expect.begin()
        dMock.expect.end()
        cMock.expect.begin()
        cMock.expect.end()
        bMock.expect.begin()
        bMock.expect.end()
        aMock.expect.begin()
        aMock.expect.end()

        a.execute(jobs=3)

    def testDiamondDependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        c, cMock = self.__createMockedAction("c")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(c)
        b.addDependency(d)
        c.addDependency(d)

        dMock.expect.begin()
        dMock.expect.end()
        with self.mocks.unordered:
            bMock.expect.begin()
            cMock.expect.begin()
        with self.mocks.unordered:
            bMock.expect.end()
            cMock.expect.end()
        aMock.expect.begin()
        aMock.expect.end()

        a.execute(jobs=3)

    def testHalfDiamondDependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a, aMock = self.__createMockedAction("a")
        b, bMock = self.__createMockedAction("b")
        d, dMock = self.__createMockedAction("d")
        a.addDependency(b)
        a.addDependency(d)
        b.addDependency(d)

        dMock.expect.begin()
        dMock.expect.end()
        bMock.expect.begin()
        bMock.expect.end()
        aMock.expect.begin()
        aMock.expect.end()

        a.execute(jobs=3)
