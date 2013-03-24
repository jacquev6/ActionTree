# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from ActionTree import Action


class DependencyCycle(unittest.TestCase):
    def testSelfDependency(self):
        a = Action(lambda: 0, "a")
        with self.assertRaises(Exception) as cm:
            a.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testShortCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        a.addDependency(b)
        with self.assertRaises(Exception) as cm:
            b.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")

    def testLongCycle(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        e = Action(lambda: 0, "e")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)
        d.addDependency(e)
        with self.assertRaises(Exception) as cm:
            e.addDependency(a)
        self.assertEqual(cm.exception.args[0], "Dependency cycle")
