# coding: utf8

# Copyright 2017-2018 Vincent Jacques <vincent@vincent-jacques.net>


import pickle
import unittest

from ActionTree import *


class Unpicklable(object):
    def __reduce__(self):
        raise pickle.PicklingError


unpicklable = Unpicklable()


class UnpicklableAction(Action):
    def __init__(self, *args, **kwds):
        super(UnpicklableAction, self).__init__(*args, **kwds)
        self.attribute = unpicklable


class UnpicklableReturnValue(Action):
    def do_execute(self, dependency_statuses):
        return unpicklable


class UnpicklableException(Action):
    def do_execute(self, dependency_statuses):
        raise Exception(unpicklable)


class PicklabilityTestCase(unittest.TestCase):
    def test_action(self):
        with self.assertRaises(pickle.PicklingError):
            execute(UnpicklableAction("x"))

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
