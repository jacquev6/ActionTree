# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
import errno
import os
import shutil
import subprocess
import unittest

import MockMockMock

from ActionTree.stock import *
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
        self.makedirs = self.mocks.replace("os.makedirs")
        self.isdir = self.mocks.replace("os.path.isdir")

    def test_label(self):
        self.assertEqual(CreateDirectory("xxx").label, "mkdir xxx")

    def test_success(self):
        self.makedirs.expect("xxx")

        CreateDirectory("xxx").execute()

    def test_directory_exists(self):
        self.makedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
        self.isdir.expect("xxx").andReturn(True)

        CreateDirectory("xxx").execute()

    def test_file_exists(self):
        self.makedirs.expect("xxx").andRaise(OSError(errno.EEXIST, "File exists"))
        self.isdir.expect("xxx").andReturn(False)

        with self.assertRaises(CompoundException):
            CreateDirectory("xxx").execute()

    def test_other_failure(self):
        self.makedirs.expect("xxx").andRaise(OSError(-1, "Foobar"))

        with self.assertRaises(CompoundException):
            CreateDirectory("xxx").execute()


class CallSubprocessTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.check_call = self.mocks.replace("subprocess.check_call")

    def test_label(self):
        self.assertEqual(CallSubprocess(["xxx", "yyy"]).label, "xxx yyy")

    def test_simple_call(self):
        self.check_call.expect(["xxx"])
        CallSubprocess(["xxx"]).execute()

    def test_call_with_several_args(self):
        self.check_call.expect(["xxx", "yyy"])
        CallSubprocess(["xxx", "yyy"]).execute()

    def test_call_with_kwds(self):
        self.check_call.expect(["xxx", "yyy"], foo="bar")
        CallSubprocess(["xxx", "yyy"], foo="bar").execute()


class DeleteFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.unlink = self.mocks.replace("os.unlink")

    def test_label(self):
        self.assertEqual(DeleteFile("xxx").label, "rm xxx")

    def test_success(self):
        self.unlink.expect("xxx")

        DeleteFile("xxx").execute()

    def test_file_does_not_exist(self):
        self.unlink.expect("xxx").andRaise(OSError(errno.ENOENT, "No such file or directory"))

        DeleteFile("xxx").execute()

    def test_other_failure(self):
        self.unlink.expect("xxx").andRaise(OSError(-1, "Foobar"))

        with self.assertRaises(CompoundException):
            DeleteFile("xxx").execute()


class CopyFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.copy = self.mocks.replace("shutil.copy")

    def test_success(self):
        self.copy.expect("from", "to")

        CopyFile("from", "to").execute()

    def test_failure(self):
        self.copy.expect("from", "to").andRaise(OSError(-1, "Foobar"))

        with self.assertRaises(CompoundException):
            CopyFile("from", "to").execute()

    def test_label(self):
        self.assertEqual(CopyFile("from", "to").label, "cp from to")


class TouchFileTestCase(TestCaseWithMocks):
    def setUp(self):
        TestCaseWithMocks.setUp(self)
        self.open = self.mocks.replace("TouchFile._open")
        self.file = self.mocks.create("FileLikeObject")
        self.utime = self.mocks.replace("os.utime")

    def test_success(self):
        self.open.expect("xxx", "ab").andReturn(self.file.object)
        self.file.expect.close()
        self.utime.expect("xxx", None)

        TouchFile("xxx").execute()

    def test_label(self):
        self.assertEqual(TouchFile("xxx").label, "touch xxx")


class NullActionTestCase(unittest.TestCase):
    def test(self):
        NullAction().execute()


class SleepTestCase(unittest.TestCase):
    def test(self):
        before = datetime.datetime.now()
        Sleep(1).execute()
        self.assertGreater(datetime.datetime.now() - before, datetime.timedelta(seconds=1))
