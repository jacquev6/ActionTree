# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
import errno
import os
import shutil
import subprocess
import unittest

import MockMockMock

from ActionTree.StockActions import *
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
        self.mockedOpen = self.mocks.replace("TouchFiles._open")
        self.mockedFile = self.mocks.create("FileLikeObject")
        self.mockedUtime = self.mocks.replace("os.utime")

    def testSuccess(self):
        self.mockedOpen.expect("xxx", "ab").andReturn(self.mockedFile.object)
        self.mockedFile.expect.close()
        self.mockedUtime.expect("xxx", None)
        self.mockedOpen.expect("yyy", "ab").andReturn(self.mockedFile.object)
        self.mockedFile.expect.close()
        self.mockedUtime.expect("yyy", None)

        TouchFiles(["xxx", "yyy"]).execute()

    def testLabel(self):
        self.assertEqual(TouchFiles(["xxx", "yyy"]).label, "touch xxx yyy")


class NullActionTestCase(unittest.TestCase):
    def test(self):
        NullAction().execute()


class SleepTestCase(unittest.TestCase):
    def test(self):
        before = datetime.datetime.now()
        Sleep(1).execute()
        self.assertGreater(datetime.datetime.now() - before, datetime.timedelta(seconds=1))
