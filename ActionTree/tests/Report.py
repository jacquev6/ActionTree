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
import cairo
import MockMockMock
import io
import hashlib
import traceback

import ActionTree
from ActionTree.Drawings import ExecutionReport


class Report(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.actionMocks = MockMockMock.Engine()
        self.actionMocks.unordered  # @todo in MockMockMock, find a better syntax to use grouping without "with" keyword

    def tearDown(self):
        self.actionMocks.tearDown()
        unittest.TestCase.tearDown(self)

    # Expect several digests because cairo may not produce exactly the same file on
    # all platorms and versions
    def __checkDrawing(self, a, width, expectedDigests):
        testName = None
        for (_, _, functionName, _) in traceback.extract_stack():
            if functionName.startswith("test"):
                testName = "Report." + functionName
                break
        self.assertIsNot(testName, None)

        r = ExecutionReport(a)
        height = r.getHeight(cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)))

        image = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(image)
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0)
        r.draw(ctx, width)
        f = io.BytesIO()
        image.write_to_png(f)
        digest = hashlib.md5(f.getvalue()).hexdigest()
        if digest not in expectedDigests.values():
            fileName = testName + ".png"
            with open(fileName, "wb") as png:
                png.write(f.getvalue())
            self.assertTrue(False, "Check file " + fileName + ". If it is OK, modify test " + testName + " to accept digest " + digest)
        f.close()

    def __createMockedAction(self, name, label, dependencies, beginTime, endTime, status):
        a = self.actionMocks.create(name)
        a.expect.label.andReturn(label)
        a.expect.beginTime.andReturn(beginTime)
        a.expect.endTime.andReturn(endTime)
        a.expect.status.andReturn(status)
        a.expect.getDependencies().andReturn(dependencies)
        return a.object

    def testComplexLabel(self):
        a = self.__createMockedAction("a", ("a", "complex", [42, "label"]), [], 10.5, 13.5, ActionTree.Action.Successful)

        self.__checkDrawing(a, 400, {"Python 2.7, Windows": "d3e010597c08e058ac27f6e50369e621", "Python 2.7, Cygwin": "ed21917ada5fea4c79b7548f5aebb329"})

    def testOneSuccessfulAction(self):
        a = self.__createMockedAction("a", "label", [], 10.5, 13.5, ActionTree.Action.Successful)

        self.__checkDrawing(a, 200, {"Python 2.7, Windows": "65815c6bcf05054c98e2b51f2775727f", "Python 2.7, Cygwin": "ddaae26c8484c33fd4faf421e0fa93d7"})

    def testOneFailedAction(self):
        a = self.__createMockedAction("a", "label", [], 10.5, 13.5, ActionTree.Action.Failed)

        self.__checkDrawing(a, 200, {"Python 2.7, Windows": "24e6d627b1b6b7610c75b6a68d9299ab", "Python 2.7, Cygwin": "ea13184dcfd75b0835232c22b0e003c8"})

    def testOneCanceledAction(self):
        a = self.__createMockedAction("a", "label", [], 10.5, 13.5, ActionTree.Action.Canceled)

        self.__checkDrawing(a, 200, {"Python 2.7, Windows": "c4d95f1bb610b3fb7e39bc818c06506e", "Python 2.7, Cygwin": "3c1bd21bf5359dd6edc03bf28f8f3cab"})
