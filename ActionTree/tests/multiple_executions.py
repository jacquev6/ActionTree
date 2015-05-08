# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest
import MockMockMock

from ActionTree import Action, CompoundException


class MultipleExecutions(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def __create_mocked_action(self, name):
        mock = self.mocks.create(name)
        action = Action(mock.object, name)
        return action, mock

    def tearDown(self):
        self.mocks.tearDown()

    def test_simple_success(self):
        repeat = 5
        a, aMock = self.__create_mocked_action("a")

        for i in range(repeat):
            aMock.expect()

        for i in range(repeat):
            a.execute()
            self.assertEqual(a.status, Action.Successful)

    def test_failure_in_middle(self):
        a, aMock = self.__create_mocked_action("a")
        b, bMock = self.__create_mocked_action("b")
        c, cMock = self.__create_mocked_action("c")
        a.add_dependency(b)
        b.add_dependency(c)

        repeat = 5
        for i in range(repeat):
            cMock.expect()
            bMock.expect().andRaise(Exception())

        for i in range(repeat):
            with self.assertRaises(CompoundException):
                a.execute()
            self.assertEqual(a.status, Action.Canceled)
            self.assertEqual(b.status, Action.Failed)
            self.assertEqual(c.status, Action.Successful)
