# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import unittest

import MockMockMock


class TestCaseWithMocks(unittest.TestCase):
    def setUp(self):
        super(TestCaseWithMocks, self).setUp()
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        self.mocks.tearDown()
        super(TestCaseWithMocks, self).tearDown()
