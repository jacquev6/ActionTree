# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

import MockMockMock


class TestCaseWithMocks(unittest.TestCase):
    def setUp(self):
        super(TestCaseWithMocks, self).setUp()
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        self.mocks.tearDown()
        super(TestCaseWithMocks, self).tearDown()
