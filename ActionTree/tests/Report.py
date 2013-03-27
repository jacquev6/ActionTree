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
    def __checkDrawing(self, r, width, expectedDigests):
        testName = None
        for (_, _, functionName, _) in traceback.extract_stack():
            if functionName.startswith("test"):
                testName = "Report." + functionName
                break
        self.assertIsNot(testName, None)

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

    def testComplexLabel(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn(("a", "complex", [42, "label"]))
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Successful)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, 400, ["d3e010597c08e058ac27f6e50369e621"])

    def testOneSuccessfulAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn("label")
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Successful)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, 200, ["65815c6bcf05054c98e2b51f2775727f"])

    def testOneFailedAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn("label")
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Failed)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, 200, ["24e6d627b1b6b7610c75b6a68d9299ab"])

    def testOneCanceledAction(self):
        a = self.mocks.create("a")

        with self.mocks.unordered:
            a.expect.getDependencies().andReturn([])
            a.expect.label.andReturn("label")
            a.expect.beginTime.andReturn(10.5)
            a.expect.endTime.andReturn(13.5)
            a.expect.status.andReturn(ActionTree.Action.Canceled)

        r = ExecutionReport(a.object)
        self.__checkDrawing(r, 200, ["c4d95f1bb610b3fb7e39bc818c06506e"])
