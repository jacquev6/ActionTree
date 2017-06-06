# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import threading
import time

from ActionTree import Action
from . import TestCaseWithMocks


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


class MultiThreadedExecutionTestCase(TestCaseWithMocks):
    def __create_mocked_action(self, name):
        mock = self.mocks.create(name)
        action = Action(ExecuteMock(mock.object), name)
        return action, mock

    def test_many_dependencies(self):
        #     a
        #    /|\
        #   / | \
        #  b  c  d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

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

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        e, eMock = self.__create_mocked_action("e")
        f, fMock = self.__create_mocked_action("f")
        a.add_dependency(b)
        b.add_dependency(c)
        c.add_dependency(d)
        d.add_dependency(e)
        e.add_dependency(f)

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

    def test_diamond_dependencies(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(d)

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

    def test_half_diamond_dependency(self):
        #     a
        #    /|
        #   b |
        #    \|
        #     d

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        d, dMock = self.__create_mocked_action("d")
        a.add_dependency(b)
        a.add_dependency(d)
        b.add_dependency(d)

        dMock.expect.begin()
        dMock.expect.end()
        bMock.expect.begin()
        bMock.expect.end()
        aMock.expect.begin()
        aMock.expect.end()

        a.execute(jobs=3)
