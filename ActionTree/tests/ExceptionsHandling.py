# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import Framework

from ActionTree import Action, CompoundException


class ExceptionsHandling(Framework.TestCase):
    def testExceptionInDependency(self):
        dependencies = "b"
        for name in dependencies:
            self.addDependency("a", name)

        e = Exception()
        self.getMock("b").expect().andRaise(e)

        with self.assertRaises(CompoundException) as cm:
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

        with self.assertRaises(CompoundException) as cm:
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

        with self.assertRaises(CompoundException) as cm:
            a.execute()
        self.assertEqual(len(cm.exception.exceptions), 1)
        self.assertTrue(cm.exception.exceptions[0] in [eb, ec, ed])
        self.assertTrue(a.canceled)
        self.assertTrue(b.failed ^ b.canceled)
        self.assertTrue(c.failed ^ c.canceled)
        self.assertTrue(d.failed ^ d.canceled)
        self.assertEqual(len([x for x in [b, c, d] if x.failed]), 1)
        self.assertEqual(len([x for x in [b, c, d] if x.canceled]), 2)
