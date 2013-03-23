# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import Framework

from ActionTree.Action import Action


class ExceptionsHandling(Framework.TestCase):
    def testExceptionInDependency(self):
        dependencies = "b"
        for name in dependencies:
            self.addDependency("a", name)

        e = Exception()
        self.getMock("b").expect().andRaise(e)

        with self.assertRaises(Action.Exception) as cm:
            self.getAction("a").execute()
        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertIs(cm.exception.exceptions[0], e)
        self.assertTrue(self.getAction("a").canceled)
        self.assertTrue(self.getAction("b").failed)

    def testExceptionsInDependencies_KeepGoing(self):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency("a", name)

        eb = Exception()
        ec = Exception()
        with self.unordered:
            self.getMock("b").expect().andRaise(eb)
            self.getMock("c").expect().andRaise(ec)
            self.getMock("d").expect()

        with self.assertRaises(Action.Exception) as cm:
            self.getAction("a").execute(keepGoing=True)
        self.assertEqual(len(cm.exception.exceptions), 2)
        self.assertTrue(eb in cm.exception.exceptions)
        self.assertTrue(ec in cm.exception.exceptions)
        self.assertTrue(self.getAction("a").canceled)
        self.assertTrue(self.getAction("b").failed)
        self.assertTrue(self.getAction("c").failed)
        self.assertTrue(self.getAction("d").successful)

    def testExceptionsInDependencies_NoKeepGoing(self):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency("a", name)

        eb = Exception()
        ec = Exception()
        ed = Exception()
        with self.unordered:
            with self.optional:
                self.getMock("b").expect().andRaise(eb)
            with self.optional:
                self.getMock("c").expect().andRaise(ec)
            with self.optional:
                self.getMock("d").expect().andRaise(ed)

        a = self.getAction("a")
        b = self.getAction("b")
        c = self.getAction("c")
        d = self.getAction("d")

        with self.assertRaises(Action.Exception) as cm:
            a.execute()
        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertTrue(cm.exception.exceptions[0] in [eb, ec, ed])
        self.assertTrue(a.canceled)
        self.assertTrue(b.failed ^ b.canceled)
        self.assertTrue(c.failed ^ c.canceled)
        self.assertTrue(d.failed ^ d.canceled)
        self.assertEqual(len([x for x in [b, c, d] if x.failed]), 1)
        self.assertEqual(len([x for x in [b, c, d] if x.canceled]), 2)
