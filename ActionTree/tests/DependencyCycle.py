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


class DependencyCycle(Framework.TestCase):
    def testSelfDependency(self):
        with self.assertRaises(Exception):
            self.addDependency("a", "a")

    def testShortCycle(self):
        self.addDependency("a", "b")
        with self.assertRaises(Exception):
            self.addDependency("b", "a")

    def testLongCycle(self):
        self.addDependency("a", "b")
        self.addDependency("b", "c")
        self.addDependency("c", "d")
        self.addDependency("d", "e")
        with self.assertRaises(Exception):
            self.addDependency("e", "a")
