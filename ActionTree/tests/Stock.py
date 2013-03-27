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
import os
import errno
import MockMockMock

from ActionTree.StockActions import CreateDirectory
from ActionTree import CompoundException

class Stock(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.mocks.tearDown()

    def testCreateDirectory(self):
        oldMakedirs = os.makedirs
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object

            mockedMakedirs.expect("xxx")
            a = CreateDirectory("xxx")
            a.execute()
        finally:
            os.makedirs = oldMakedirs

    def testCreateExistingDirectory(self):
        oldMakedirs = os.makedirs
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object

            mockedMakedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
            a = CreateDirectory("xxx")
            a.execute()
        finally:
            os.makedirs = oldMakedirs

    def testDirectoryCreationFailure(self):
        oldMakedirs = os.makedirs
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object

            e = OSError(-1, "Foobar")
            mockedMakedirs.expect("xxx").andRaise(e)
            a = CreateDirectory("xxx")
            with self.assertRaises(CompoundException) as cm:
                a.execute()
            self.assertIs(cm.exception.exceptions[0], e)
        finally:
            os.makedirs = oldMakedirs
