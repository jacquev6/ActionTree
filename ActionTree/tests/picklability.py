# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import pickle
import unittest
import sys
import tempfile

from ActionTree import *
from . import *


class Unpicklable(object):
    def __reduce__(self):
        raise pickle.PicklingError


unpicklable = Unpicklable()


class UnpicklableReturnValue(Action):
    def do_execute(self):
        return unpicklable  # pragma no cover (Test code executed in child process)


class UnpicklableException(Action):
    def do_execute(self):
        raise Exception(unpicklable)  # pragma no cover (Test code executed in child process)


class PicklabilityTestCase(ActionTreeTestCase):
    def test_action(self):
        with self.assertRaises(pickle.PicklingError):
            execute(self._action(unpicklable))

    def test_return_value(self):
        with self.assertRaises(pickle.PicklingError):
            # DO NOT use self._action(return_value=unpicklable)
            # because the *Action* would be unpicklable and we're testing what happens
            # when the *return value* is unpicklable
            execute(UnpicklableReturnValue("x"))

    def test_exception(self):
        with self.assertRaises(pickle.PicklingError):
            # DO NOT use self._action(return_value=unpicklable)
            # because the *Action* would be unpicklable and we're testing what happens
            # when the *exception* is unpicklable
            execute(UnpicklableException("x"))
