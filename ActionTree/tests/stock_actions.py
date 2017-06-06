# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import datetime
import errno
import unittest

from ActionTree.stock import *
from ActionTree import CompoundException


class PatchingTestCase(unittest.TestCase):
    def patch(self, *args, **kwds):
        patcher = unittest.mock.patch(*args, **kwds)
        patched = patcher.start()
        self.addCleanup(patcher.stop)
        return patched


class CreateDirectoryTestCase(PatchingTestCase):
    def setUp(self):
        self.makedirs = self.patch("os.makedirs")
        self.isdir = self.patch("os.path.isdir")

    def test_label(self):
        self.assertEqual(CreateDirectory("xxx").label, "mkdir xxx")

        self.makedirs.assert_not_called()
        self.isdir.assert_not_called()

    def test_success(self):
        self.makedirs.expect("xxx")

        CreateDirectory("xxx").execute()

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_not_called()

    def test_directory_exists(self):
        self.makedirs.side_effect = OSError(errno.EEXIST, "File exists")
        self.isdir.return_value = True

        CreateDirectory("xxx").execute()

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_called_once_with("xxx")

    def test_file_exists(self):
        self.makedirs.side_effect = OSError(errno.EEXIST, "File exists")
        self.isdir.return_value = False

        with self.assertRaises(CompoundException):
            CreateDirectory("xxx").execute()

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_called_once_with("xxx")

    def test_other_failure(self):
        self.makedirs.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(CompoundException):
            CreateDirectory("xxx").execute()

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_not_called()


class CallSubprocessTestCase(PatchingTestCase):
    def setUp(self):
        self.check_call = self.patch("subprocess.check_call")

    def test_label(self):
        self.assertEqual(CallSubprocess(["xxx", "yyy"]).label, "xxx yyy")

        self.check_call.assert_not_called()

    def test_simple_call(self):
        CallSubprocess(["xxx"]).execute()

        self.check_call.assert_called_once_with(["xxx"])

    def test_call_with_several_args(self):
        self.check_call.expect(["xxx", "yyy"])
        CallSubprocess(["xxx", "yyy"]).execute()

        self.check_call.assert_called_once_with(["xxx", "yyy"])

    def test_call_with_kwds(self):
        CallSubprocess(["xxx", "yyy"], foo="bar").execute()

        self.check_call.assert_called_once_with(["xxx", "yyy"], foo="bar")


class DeleteFileTestCase(PatchingTestCase):
    def setUp(self):
        self.unlink = self.patch("os.unlink")

    def test_label(self):
        self.assertEqual(DeleteFile("xxx").label, "rm xxx")

        self.unlink.assert_not_called()

    def test_success(self):
        DeleteFile("xxx").execute()

        self.unlink.assert_called_once_with("xxx")

    def test_file_does_not_exist(self):
        self.unlink.side_effect = OSError(errno.ENOENT, "No such file or directory")

        DeleteFile("xxx").execute()

        self.unlink.assert_called_once_with("xxx")

    def test_other_failure(self):
        self.unlink.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(CompoundException):
            DeleteFile("xxx").execute()

        self.unlink.assert_called_once_with("xxx")


class CopyFileTestCase(PatchingTestCase):
    def setUp(self):
        self.copy = self.patch("shutil.copy")

    def test_label(self):
        self.assertEqual(CopyFile("from", "to").label, "cp from to")

        self.copy.assert_not_called()

    def test_success(self):
        CopyFile("from", "to").execute()

        self.copy.assert_called_once_with("from", "to")

    def test_failure(self):
        self.copy.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(CompoundException):
            CopyFile("from", "to").execute()

        self.copy.assert_called_once_with("from", "to")


class TouchFileTestCase(PatchingTestCase):
    def setUp(self):
        self.open = self.patch("ActionTree.stock.open", new=unittest.mock.mock_open(), create=True)
        self.utime = self.patch("os.utime")

    def test_label(self):
        self.assertEqual(TouchFile("xxx").label, "touch xxx")

        self.open.assert_not_called()
        self.utime.assert_not_called()

    def test_success(self):
        TouchFile("xxx").execute()

        self.open.assert_called_once_with("xxx", "ab")
        self.open().close.assert_called_once_with()
        self.utime.assert_called_once_with("xxx", None)


class NullActionTestCase(unittest.TestCase):
    def test(self):
        NullAction().execute()


class SleepTestCase(PatchingTestCase):
    def setUp(self):
        self.sleep = self.patch("time.sleep")

    def test(self):
        Sleep(1).execute()

        self.sleep.assert_called_once_with(1)
