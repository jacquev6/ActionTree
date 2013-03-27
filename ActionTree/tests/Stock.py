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

class CreateDirectoryTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.mocks.tearDown()

    def testSuccess(self):
        oldMakedirs = os.makedirs
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object

            mockedMakedirs.expect("xxx")
            a = CreateDirectory("xxx")
            a.execute()
        finally:
            os.makedirs = oldMakedirs

    def testDirectoryExists(self):
        oldMakedirs = os.makedirs
        oldOsPathIsDir = os.path.isdir
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object
            mockedIsDir = self.mocks.create("os.path.isdir")
            os.path.isdir = mockedIsDir.object

            mockedMakedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
            mockedIsDir.expect("xxx").andReturn(True)
            a = CreateDirectory("xxx")
            a.execute()
        finally:
            os.makedirs = oldMakedirs
            os.path.isdir = oldOsPathIsDir

    def testFileExists(self):
        oldMakedirs = os.makedirs
        oldOsPathIsDir = os.path.isdir
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object
            mockedIsDir = self.mocks.create("os.path.isdir")
            os.path.isdir = mockedIsDir.object

            mockedMakedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
            mockedIsDir.expect("xxx").andReturn(False)

            a = CreateDirectory("xxx")
            with self.assertRaises(CompoundException) as cm:
                a.execute()
        finally:
            os.makedirs = oldMakedirs
            os.path.isdir = oldOsPathIsDir

    def testOtherFailure(self):
        oldMakedirs = os.makedirs
        try:
            mockedMakedirs = self.mocks.create("os.makedirs")
            os.makedirs = mockedMakedirs.object

            mockedMakedirs.expect("xxx").andRaise(OSError(-1, "Foobar"))

            a = CreateDirectory("xxx")
            with self.assertRaises(CompoundException) as cm:
                a.execute()
        finally:
            os.makedirs = oldMakedirs
