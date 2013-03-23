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


class MultipleExecutions(Framework.TestCase):
    def testSimpleSuccess(self):
        repeat = 5
        for i in range(repeat):
            self.getMock("a").expect()

        for i in range(repeat):
            self.getAction("a").execute()

    def testFailureInMiddle(self):
        self.addDependency("a", "b")
        self.addDependency("b", "c")

        repeat = 5
        for i in range(repeat):
            self.getMock("c").expect()
            self.getMock("b").expect().andRaise(Exception())

        for i in range(repeat):
            with self.assertRaises(CompoundException):
                self.getAction("a").execute()
