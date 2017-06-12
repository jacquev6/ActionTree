# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import ctypes
import subprocess
import sys
import unittest

from ActionTree import *


libc = ctypes.CDLL(None)


class PrintAction(Action):
    def do_execute(self):
        print("printed on stdout")


class PrintStderrAction(Action):
    def do_execute(self):
        print("printed on stderr", file=sys.stderr)


class EchoAction(Action):
    def do_execute(self):
        subprocess.check_call(["echo", "echoed on stdout"])


class PutsAction(Action):
    def do_execute(self):
        libc.puts(b"putsed on stdout")


class ExecutionTestCase(unittest.TestCase):
    def test_print(self):
        a = PrintAction("a")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "printed on stdout\n")

    def test_print_stderr(self):
        a = PrintStderrAction("a")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "printed on stderr\n")

    def test_echo(self):
        a = EchoAction("a")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "echoed on stdout\n")

    def test_puts(self):
        a = PutsAction("a")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "putsed on stdout\n")
