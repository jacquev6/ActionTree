# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import os
import unittest

from ActionTree import *
from ActionTree.stock import *


class ChdirAction(Action):
    def do_execute(self, dependency_statuses):
        print(os.getcwd())
        os.chdir("/")


class ChangeEnvironAction(Action):
    def do_execute(self, dependency_statuses):
        print(os.environ.get("FOO"))
        os.environ["FOO"] = "bar"


class ProcessWideStateTestCase(unittest.TestCase):
    def test_working_directory(self):
        a = ChdirAction("a")
        b = ChdirAction("b")
        a.add_dependency(b)

        report = execute(a)
        self.assertEqual(report.get_action_status(a).output, report.get_action_status(b).output)

    def test_environment(self):
        a = ChangeEnvironAction("a")
        b = ChangeEnvironAction("b")
        a.add_dependency(b)

        report = execute(a)
        self.assertEqual(report.get_action_status(a).output, report.get_action_status(b).output)
