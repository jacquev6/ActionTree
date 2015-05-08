# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import threading
import time
import unittest
import MockMockMock

from ActionTree import Action


class Execution(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __create_mocked_action(self, name):
        mock = self.mocks.create(name)
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def test_simple_execution(self):
        a, aMock = self.__create_mocked_action("a")

        aMock.expect()

        self.assertEqual(a.status, Action.Pending)
        a.execute()
        self.assertEqual(a.status, Action.Successful)

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
            bMock.expect()
            cMock.expect()
            dMock.expect()
        aMock.expect()

        a.execute()

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

        fMock.expect()
        eMock.expect()
        dMock.expect()
        cMock.expect()
        bMock.expect()
        aMock.expect()

        a.execute()

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

        dMock.expect()
        with self.mocks.unordered:
            bMock.expect()
            cMock.expect()
        aMock.expect()

        a.execute()

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

        dMock.expect()
        bMock.expect()
        aMock.expect()

        a.execute()

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

        with self.mocks.unordered:
            dMock.expect()
            eMock.expect()
        # In previous implementation in ViDE, deepest leaves were
        # executed first. It is not mandatory, but it make cleaner
        # executions, because similar tasks are executed at once.
        # To restore this behavior if needed, uncomment next line
        # with self.mocks.unordered:
        # This would have to be done also in getPreview
            bMock.expect()
            cMock.expect()
        aMock.expect()

        a.execute()
