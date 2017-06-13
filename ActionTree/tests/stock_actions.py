# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import errno
import pickle
import subprocess
import unittest

from ActionTree.stock import *
from ActionTree import *


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

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(CreateDirectory("xxx")), bytes)

    def test_success(self):
        self.makedirs.expect("xxx")

        CreateDirectory("xxx").do_execute({})

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_not_called()

    def test_directory_exists(self):
        self.makedirs.side_effect = OSError(errno.EEXIST, "File exists")
        self.isdir.return_value = True

        CreateDirectory("xxx").do_execute({})

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_called_once_with("xxx")

    def test_file_exists(self):
        self.makedirs.side_effect = OSError(errno.EEXIST, "File exists")
        self.isdir.return_value = False

        with self.assertRaises(OSError):
            CreateDirectory("xxx").do_execute({})

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_called_once_with("xxx")

    def test_other_failure(self):
        self.makedirs.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(OSError):
            CreateDirectory("xxx").do_execute({})

        self.makedirs.assert_called_once_with("xxx")
        self.isdir.assert_not_called()


class CallSubprocessTestCase(PatchingTestCase):
    def setUp(self):
        self.check_call = self.patch("subprocess.check_call")

    def test_label(self):
        self.assertEqual(CallSubprocess(["xxx", "yyy"]).label, "xxx yyy")

        self.check_call.assert_not_called()

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(CallSubprocess(["xxx", "yyy"])), bytes)

    def test_simple_call(self):
        CallSubprocess(["xxx"]).do_execute({})

        self.check_call.assert_called_once_with(["xxx"])

    def test_call_with_several_args(self):
        self.check_call.expect(["xxx", "yyy"])
        CallSubprocess(["xxx", "yyy"]).do_execute({})

        self.check_call.assert_called_once_with(["xxx", "yyy"])

    def test_call_with_kwds(self):
        CallSubprocess(["xxx", "yyy"], foo="bar").do_execute({})

        self.check_call.assert_called_once_with(["xxx", "yyy"], foo="bar")

    def test_called_process_error(self):
        self.check_call.side_effect = subprocess.CalledProcessError(1, ["false"], None)

        with self.assertRaises(CalledProcessError) as catcher:
            CallSubprocess(["false"]).do_execute({})
        self.assertEqual(catcher.exception.args, (1, ["false"], None))


class CallSubprocessForRealTestCase(unittest.TestCase):
    def test_called_process_error(self):
        with self.assertRaises(CompoundException) as catcher:
            execute(CallSubprocess(["false"]))
        self.assertEqual(catcher.exception.exceptions[0].args, (1, ["false"], None))


class DeleteFileTestCase(PatchingTestCase):
    def setUp(self):
        self.unlink = self.patch("os.unlink")

    def test_label(self):
        self.assertEqual(DeleteFile("xxx").label, "rm xxx")

        self.unlink.assert_not_called()

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(DeleteFile("xxx")), bytes)

    def test_success(self):
        DeleteFile("xxx").do_execute({})

        self.unlink.assert_called_once_with("xxx")

    def test_file_does_not_exist(self):
        self.unlink.side_effect = OSError(errno.ENOENT, "No such file or directory")

        DeleteFile("xxx").do_execute({})

        self.unlink.assert_called_once_with("xxx")

    def test_other_failure(self):
        self.unlink.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(OSError):
            DeleteFile("xxx").do_execute({})

        self.unlink.assert_called_once_with("xxx")


class CopyFileTestCase(PatchingTestCase):
    def setUp(self):
        self.copy = self.patch("shutil.copy")

    def test_label(self):
        self.assertEqual(CopyFile("from", "to").label, "cp from to")

        self.copy.assert_not_called()

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(CopyFile("from", "to")), bytes)

    def test_success(self):
        CopyFile("from", "to").do_execute({})

        self.copy.assert_called_once_with("from", "to")

    def test_failure(self):
        self.copy.side_effect = OSError(-1, "Foobar")

        with self.assertRaises(OSError):
            CopyFile("from", "to").do_execute({})

        self.copy.assert_called_once_with("from", "to")


class TouchFileTestCase(PatchingTestCase):
    def setUp(self):
        self.open = self.patch("ActionTree.stock.open", new=unittest.mock.mock_open(), create=True)
        self.utime = self.patch("os.utime")

    def test_label(self):
        self.assertEqual(TouchFile("xxx").label, "touch xxx")

        self.open.assert_not_called()
        self.utime.assert_not_called()

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(TouchFile("xxx")), bytes)

    def test_success(self):
        TouchFile("xxx").do_execute({})

        self.open.assert_called_once_with("xxx", "ab")
        self.open().close.assert_called_once_with()
        self.utime.assert_called_once_with("xxx", None)


class NullActionTestCase(unittest.TestCase):
    def test_label(self):
        self.assertIsNone(NullAction().label)

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(NullAction()), bytes)

    def test(self):
        NullAction().do_execute({})


class SleepTestCase(PatchingTestCase):
    def setUp(self):
        self.sleep = self.patch("time.sleep")

    def test_label(self):
        self.assertEqual(Sleep(1).label, "sleep 1")

        self.sleep.assert_not_called()

    def test_pickle(self):
        self.assertIsInstance(pickle.dumps(Sleep(1)), bytes)

    def test(self):
        Sleep(1).do_execute({})

        self.sleep.assert_called_once_with(1)
