# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import threading
import time
import unittest

from ActionTree import *


class ExecuteMock:
    def __init__(self, lock, mock):
        self.__mock = mock
        self.__lock = lock

    def __call__(self):
        with self.__lock:
            self.__mock.begin()
        time.sleep(0.1)
        with self.__lock:
            self.__mock.end()


class MultiThreadedExecutionTestCase(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.lock = threading.Lock()

    def __create_mocked_action(self, name):
        mock = unittest.mock.Mock()
        mock.begin.side_effect = lambda: self.calls.append("B" + name)
        mock.end.side_effect = lambda: self.calls.append("E" + name)
        action = ActionFromCallable(ExecuteMock(self.lock, mock), name)
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

        execute(a, jobs=3)

        aMock.begin.assert_called_once_with()
        aMock.end.assert_called_once_with()
        bMock.begin.assert_called_once_with()
        bMock.end.assert_called_once_with()
        cMock.begin.assert_called_once_with()
        cMock.end.assert_called_once_with()
        dMock.begin.assert_called_once_with()
        dMock.end.assert_called_once_with()

        self.assertEqual(sorted(self.calls[0:3]), ["Bb", "Bc", "Bd"])
        self.assertEqual(sorted(self.calls[3:6]), ["Eb", "Ec", "Ed"])
        self.assertEqual(self.calls[6:], ["Ba", "Ea"])

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

        execute(a, jobs=3)

        aMock.begin.assert_called_once_with()
        aMock.end.assert_called_once_with()
        bMock.begin.assert_called_once_with()
        bMock.end.assert_called_once_with()
        cMock.begin.assert_called_once_with()
        cMock.end.assert_called_once_with()
        dMock.begin.assert_called_once_with()
        dMock.end.assert_called_once_with()
        eMock.begin.assert_called_once_with()
        eMock.end.assert_called_once_with()
        fMock.begin.assert_called_once_with()
        fMock.end.assert_called_once_with()

        self.assertEqual(self.calls, ["Bf", "Ef", "Be", "Ee", "Bd", "Ed", "Bc", "Ec", "Bb", "Eb", "Ba", "Ea"])

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

        execute(a, jobs=3)

        aMock.begin.assert_called_once_with()
        aMock.end.assert_called_once_with()
        bMock.begin.assert_called_once_with()
        bMock.end.assert_called_once_with()
        cMock.begin.assert_called_once_with()
        cMock.end.assert_called_once_with()
        dMock.begin.assert_called_once_with()
        dMock.end.assert_called_once_with()

        self.assertEqual(self.calls[0:2], ["Bd", "Ed"])
        self.assertEqual(sorted(self.calls[2:4]), ["Bb", "Bc"])
        self.assertEqual(sorted(self.calls[4:6]), ["Eb", "Ec"])
        self.assertEqual(self.calls[6:], ["Ba", "Ea"])

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

        execute(a, jobs=3)

        self.assertEqual(self.calls, ["Bd", "Ed", "Bb", "Eb", "Ba", "Ea"])

    def test_two_deep_branches(self):
        #     a
        #    / \
        #   b   c
        #   |   |
        #   d   e

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        d, dMock = self.__create_mocked_action("d")
        e, eMock = self.__create_mocked_action("e")
        a.add_dependency(b)
        a.add_dependency(c)
        b.add_dependency(d)
        c.add_dependency(e)

        execute(a, jobs=3)

        aMock.begin.assert_called_once_with()
        aMock.end.assert_called_once_with()
        bMock.begin.assert_called_once_with()
        bMock.end.assert_called_once_with()
        cMock.begin.assert_called_once_with()
        cMock.end.assert_called_once_with()
        dMock.begin.assert_called_once_with()
        dMock.end.assert_called_once_with()
        eMock.begin.assert_called_once_with()
        eMock.end.assert_called_once_with()

        self.assertEqual(sorted(self.calls[0:2]), ["Bd", "Be"])
        self.assertEqual(sorted(self.calls[2:6]), ["Bb", "Bc", "Ed", "Ee"])
        self.assertEqual(sorted(self.calls[6:8]), ["Eb", "Ec"])
        self.assertEqual(self.calls[8:], ["Ba", "Ea"])

    def test_default_jobs_count(self):
        # Default jobs count (when jobs < 0) is at least 2 even on a single core machine
        #     a
        #    /|
        #   / |
        #  b  c

        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        a.add_dependency(b)
        a.add_dependency(c)

        execute(a, jobs=-1)

        aMock.begin.assert_called_once_with()
        aMock.end.assert_called_once_with()
        bMock.begin.assert_called_once_with()
        bMock.end.assert_called_once_with()
        cMock.begin.assert_called_once_with()
        cMock.end.assert_called_once_with()

        self.assertEqual(sorted(self.calls[0:2]), ["Bb", "Bc"])
        self.assertEqual(sorted(self.calls[2:4]), ["Eb", "Ec"])
        self.assertEqual(self.calls[4:], ["Ba", "Ea"])
