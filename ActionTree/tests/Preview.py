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


class Preview(unittest.TestCase):
    def testGetDependenciesAndLabelsAreNotOnlyEqualButSame(self):
        bLabel = ("b",)
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, bLabel)
        a.addDependency(b)

        otherB, = a.getDependencies()
        self.assertIs(otherB, b)
        self.assertIs(otherB.label, bLabel)

    def testSimplePreview(self):
        a = Action(lambda: 0, "a")
        self.assertEqual(a.getPreview(), ["a"])

    def testTypedLabel(self):
        a = Action(lambda: 0, ("a", "curious", "label", 42))
        self.assertEqual(a.getPreview(), [("a", "curious", "label", 42)])

    def testNoneLabel(self):
        a = Action(lambda: 0, None)
        self.assertEqual(a.getPreview(), [None])

    def testDeepDependency(self):
        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)

        self.assertEqual(a.getPreview(), ["d", "c", "b", "a"])

    def testDeepDependencyWithDuplicatedLabel(self):
        a = Action(lambda: 0, "label")
        b = Action(lambda: 0, "label")
        c = Action(lambda: 0, "label")
        d = Action(lambda: 0, "label")
        a.addDependency(b)
        b.addDependency(c)
        c.addDependency(d)

        self.assertEqual(a.getPreview(), ["label", "label", "label", "label"])

    def testDiamondDependency(self):
        #     a
        #    / \
        #   b   c
        #    \ /
        #     d

        a = Action(lambda: 0, "a")
        b = Action(lambda: 0, "b")
        c = Action(lambda: 0, "c")
        d = Action(lambda: 0, "d")
        a.addDependency(b)
        a.addDependency(c)
        b.addDependency(d)
        c.addDependency(d)

        self.assertIn(a.getPreview(), [["d", "c", "b", "a"], ["d", "b", "c", "a"]])
