# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import threading
import time

import Framework

from ActionTree import Action


class ExecuteMock:
    def __init__(self, mock):
        self.__mock = mock
        self.__lock = threading.Lock()

    def __call__(self):
        with self.__lock:
            self.__mock.begin()
        time.sleep(0.1)
        with self.__lock:
            self.__mock.end()


class ThreadingTestCase:
    def testManyDependencies(self):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency("a", name)

        self.expectManyDependencies(dependencies)

        self.executeAction(self.getAction("a"))

    def testDeepDependencies(self):
        self.addDependency("a", "b")
        self.addDependency("b", "c")
        self.addDependency("c", "d")
        self.addDependency("d", "e")
        self.addDependency("e", "f")

        self.expectDeepDependencies()

        self.executeAction(self.getAction("a"))

    def testDiamondDependencies(self):
        self.addDependency("a", "b")
        self.addDependency("a", "c")
        self.addDependency("b", "d")
        self.addDependency("c", "d")

        self.expectDiamondDependencies()

        self.executeAction(self.getAction("a"))

    def testHalfDiamondDependency(self):
        self.addDependency("a", "b")
        self.addDependency("a", "d")
        self.addDependency("b", "d")

        self.expectHalfDiamondDependencies()

        self.executeAction(self.getAction("a"))


class SingleThread(Framework.TestCase, ThreadingTestCase):
    def executeAction(self, action):
        action.execute()

    def __expectAction(self, name):
        self.getMock(name).expect()

    def expectManyDependencies(self, dependencies):
        with self.unordered:
            for name in dependencies:
                self.__expectAction(name)
        self.__expectAction("a")

    def expectDeepDependencies(self):
        self.__expectAction("f")
        self.__expectAction("e")
        self.__expectAction("d")
        self.__expectAction("c")
        self.__expectAction("b")
        self.__expectAction("a")

    def expectDiamondDependencies(self):
        self.__expectAction("d")
        with self.unordered:
            self.__expectAction("b")
            self.__expectAction("c")
        self.__expectAction("a")

    def expectHalfDiamondDependencies(self):
        self.__expectAction("d")
        self.__expectAction("b")
        self.__expectAction("a")


class ThreadPool(Framework.TestCase, ThreadingTestCase):
    def callableFromMock(self, m):
        return ExecuteMock(m)

    def executeAction(self, action):
        action.execute(jobs=3)

    def __expectBegin(self, name):
        self.getMock(name).expect.begin()

    def __expectEnd(self, name):
        self.getMock(name).expect.end()

    def expectManyDependencies(self, dependencies):
        with self.unordered:
            for name in dependencies:
                self.__expectBegin(name)
        with self.unordered:
            for name in dependencies:
                self.__expectEnd(name)
        self.__expectBegin("a")
        self.__expectEnd("a")

    def expectDiamondDependencies(self):
        self.__expectBegin("d")
        self.__expectEnd("d")
        with self.unordered:
            self.__expectBegin("b")
            self.__expectBegin("c")
        with self.unordered:
            self.__expectEnd("b")
            self.__expectEnd("c")
        self.__expectBegin("a")
        self.__expectEnd("a")

    def expectHalfDiamondDependencies(self):
        self.__expectBegin("d")
        self.__expectEnd("d")
        self.__expectBegin("b")
        self.__expectEnd("b")
        self.__expectBegin("a")
        self.__expectEnd("a")

    def expectDeepDependencies(self):
        self.__expectBegin("f")
        self.__expectEnd("f")
        self.__expectBegin("e")
        self.__expectEnd("e")
        self.__expectBegin("d")
        self.__expectEnd("d")
        self.__expectBegin("c")
        self.__expectEnd("c")
        self.__expectBegin("b")
        self.__expectEnd("b")
        self.__expectBegin("a")
        self.__expectEnd("a")
