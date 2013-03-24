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
        self.mocks = MockMockMock.Engine()

    def tearDown(self):
        self.mocks.tearDown()
        unittest.TestCase.tearDown(self)

    # Expect several digests because cairo may not produce exactly the same file on
    # all platorms and versions
    def __checkDrawing(self, r, expectedDigests):
        testName = None
        for (_, _, functionName, _) in traceback.extract_stack():
            if functionName.startswith("test"):
                testName = "Report." + functionName
                break
        self.assertIsNot(testName, None)

        width = 200
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
        if digest not in expectedDigests:
            fileName = testName + ".png"
            with open(fileName, "wb") as png:
                png.write(f.getvalue())
            self.assertTrue(False, "Check file " + fileName + ". If it is OK, modify test " + testName + " to accept digest " + digest)
        f.close()

    def testOneSuccessfulAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn(("a", "complex", ["label"]))
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Successful)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, ["1c2561544692d635c0968b07f29828ec"])

    def testOneFailedAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn(("a", "complex", ["label"]))
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Failed)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, ["15e53eecf46a47bb06f253bf780919a6"])

    def testOneCanceledAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn(("a", "complex", ["label"]))
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Canceled)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, ["fbd166ddbd7faf46c304d6252e67191b"])
