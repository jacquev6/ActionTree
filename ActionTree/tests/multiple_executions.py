# coding: utf8

# Copyright 2015-2018 Vincent Jacques <vincent@vincent-jacques.net>


from ActionTree import *
from . import *


class MultipleExecutionsTestCase(ActionTreeTestCase):
    REPEAT = 5

    def test_simple_success(self):
        a = self._action("a")

        for i in range(self.REPEAT):
            report = execute(a)
            self.assertEqual(report.get_action_status(a).status, SUCCESSFUL)

        self.assertEventsEqual("a " * self.REPEAT)

    def test_failure_in_middle(self):
        a = self._action("a")
        b = self._action("b", exception=Exception())
        c = self._action("c")
        a.add_dependency(b)
        b.add_dependency(c)

        for i in range(self.REPEAT):
            with self.assertRaises(CompoundException) as catcher:
                execute(a)
            report = catcher.exception.execution_report
            self.assertEqual(report.get_action_status(a).status, CANCELED)
            self.assertEqual(report.get_action_status(b).status, FAILED)
            self.assertEqual(report.get_action_status(c).status, SUCCESSFUL)

        self.assertEventsEqual("c b " * self.REPEAT)
