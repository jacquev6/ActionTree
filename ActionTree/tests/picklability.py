# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import pickle
import unittest
import sys

from ActionTree import *
from . import *


class NonPicklableAction(Action):  # pragma no cover (Test code)
    def __init__(self):
        super(NonPicklableAction, self).__init__(lambda: ())

    def do_execute(self):
        pass


class NonPicklableReturnValue(Action):  # pragma no cover (Test code)
    def __init__(self):
        super(NonPicklableReturnValue, self).__init__("x")

    def do_execute(self):
        return lambda: ()


class NonPicklableException(Action):  # pragma no cover (Test code)
    def __init__(self):
        super(NonPicklableException, self).__init__("x")

    def do_execute(self):
        raise Exception(lambda: ())


if sys.version_info[0] == 2:
    PicklingError = pickle.PicklingError
else:  # pragma no cover (Test code)
    PicklingError = AttributeError


class PicklabilityTestCase(ActionTreeTestCase):
    def test_action(self):
        with self.assertRaises(PicklingError):
            execute(NonPicklableAction())

    def test_return_value(self):
        with self.assertRaises(PicklingError):
            execute(NonPicklableReturnValue())

    def test_exception(self):
        with self.assertRaises(PicklingError):
            execute(NonPicklableException())
