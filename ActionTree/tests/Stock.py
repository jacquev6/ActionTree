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
import shutil
import subprocess
import MockMockMock

from ActionTree.StockActions import CreateDirectory, CallSubprocess, DeleteFile, CopyFile, TouchFile
from ActionTree import CompoundException


class TestCaseWithMocks(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.mocks.tearDown()


class CreateDirectoryTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.mockedMakedirs = self.mocks.create("os.makedirs")
        self.mockedIsDir = self.mocks.create("os.path.isdir")
        self.oldMakedirs = os.makedirs
        self.oldOsPathIsDir = os.path.isdir
        os.makedirs = self.mockedMakedirs.object
        os.path.isdir = self.mockedIsDir.object

    def tearDown(self):
        TestCaseWithMocks.tearDown(self)
        os.makedirs = self.oldMakedirs
        os.path.isdir = self.oldOsPathIsDir

    def testLabel(self):
        self.assertEqual(CreateDirectory("xxx").label, "mkdir xxx")

    def testSuccess(self):
        self.mockedMakedirs.expect("xxx")

        CreateDirectory("xxx").execute()

    def testDirectoryExists(self):
        self.mockedMakedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
        self.mockedIsDir.expect("xxx").andReturn(True)

        CreateDirectory("xxx").execute()

    def testFileExists(self):
        self.mockedMakedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
        self.mockedIsDir.expect("xxx").andReturn(False)

        self.assertRaises(CompoundException, CreateDirectory("xxx").execute)

    def testOtherFailure(self):
        self.mockedMakedirs.expect("xxx").andRaise(OSError(-1, "Foobar"))

        self.assertRaises(CompoundException, CreateDirectory("xxx").execute)


class CallSubprocessTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.mockedCheckedCall = self.mocks.create("subprocess.check_call")
        self.oldCheckCall = subprocess.check_call
        subprocess.check_call = self.mockedCheckedCall.object

    def tearDown(self):
        TestCaseWithMocks.tearDown(self)
        subprocess.check_call = self.oldCheckCall

    def testLabel(self):
        self.assertEqual(CallSubprocess("xxx", "yyy").label, "xxx yyy")

    def testSimpleCall(self):
        self.mockedCheckedCall.expect(["xxx"])
        CallSubprocess("xxx").execute()

    def testCallWithSeveralArgs(self):
        self.mockedCheckedCall.expect(["xxx", "yyy"])
        CallSubprocess("xxx", "yyy").execute()

    def testCallWithKwds(self):
        self.mockedCheckedCall.expect(["xxx", "yyy"], foo="bar")
        CallSubprocess("xxx", "yyy", foo="bar").execute()


class DeleteFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.mockedUnlink = self.mocks.create("os.unlink")
        self.oldUnlink = os.unlink
        os.unlink = self.mockedUnlink.object

    def tearDown(self):
        TestCaseWithMocks.tearDown(self)
        os.unlink = self.oldUnlink

    def testLabel(self):
        self.assertEqual(DeleteFile("xxx").label, "rm xxx")

    def testSuccess(self):
        self.mockedUnlink.expect("xxx")

        DeleteFile("xxx").execute()

    def testFileDoesNotExist(self):
        self.mockedUnlink.expect("xxx").andRaise(OSError(errno.ENOENT, "No such file or directory"))

        DeleteFile("xxx").execute()

    def testOtherFailure(self):
        self.mockedUnlink.expect("xxx").andRaise(OSError(-1, "Foobar"))

        self.assertRaises(CompoundException, DeleteFile("xxx").execute)


class CopyFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.mockedCopy = self.mocks.create("shutil.copy")
        self.oldCopy = shutil.copy
        shutil.copy = self.mockedCopy.object

    def tearDown(self):
        TestCaseWithMocks.tearDown(self)
        shutil.copy = self.oldCopy

    def testSuccess(self):
        self.mockedCopy.expect("from", "to")

        CopyFile("from", "to").execute()

    def testFailure(self):
        self.mockedCopy.expect("from", "to").andRaise(OSError(-1, "Foobar"))

        self.assertRaises(CompoundException, CopyFile("from", "to").execute)

    def testLabel(self):
        self.assertEqual(CopyFile("from", "to").label, "cp from to")


class TouchFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.mockedOpen = self.mocks.create("open")
        self.mockedFile = self.mocks.create("FileLikeObject")
        self.mockedUtime = self.mocks.create("os.utime")
        self.oldOpen = TouchFile._open
        self.oldUtime = os.utime
        TouchFile._open = self.mockedOpen.object
        os.utime = self.mockedUtime.object

    def tearDown(self):
        TestCaseWithMocks.tearDown(self)
        TouchFile._open = self.oldOpen
        os.utime = self.oldUtime

    def testSuccess(self):
        self.mockedOpen.expect("xxx", "ab").andReturn(self.mockedFile.object)
        self.mockedFile.expect.close()
        self.mockedUtime.expect("xxx", None)

        TouchFile("xxx").execute()

    def testLabel(self):
        self.assertEqual(TouchFile("xxx").label, "touch xxx")
