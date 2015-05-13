# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import cairo
import hashlib
import io
import os
import traceback
import unittest

import MockMockMock

import ActionTree
from ActionTree.drawings import ExecutionReport


class ReportTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.actionMocks = MockMockMock.Engine()
        self.actionMocks.unordered  # @todo in MockMockMock, find a better syntax to use grouping without "with" keyword

    def tearDown(self):
        self.actionMocks.tearDown()
        unittest.TestCase.tearDown(self)

    # Expect several digests because cairo may not produce exactly the same file on
    # all platorms and versions
    def __check_drawing(self, a, width, *allowedDigests):
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
        if digest not in allowedDigests:
            fileName = os.path.join("ActionTree", "tests", "drawings", testName + "." + digest + ".png")
            with open(fileName, "wb") as png:
                png.write(f.getvalue())
            self.assertTrue(False, "Check file " + fileName + ".")
        f.close()

    def __create_mocked_action(self, name, label, dependencies, beginTime, endTime, status):
        a = self.actionMocks.create(name)
        a.expect.label.andReturn(label)
        a.expect.beginTime.andReturn(beginTime)
        a.expect.endTime.andReturn(endTime)
        a.expect.status.andReturn(status)
        a.expect.getDependencies().andReturn(dependencies)
        return a.object

    def test_complex_label(self):
        a = self.__create_mocked_action("a", ("a", "complex", [42, "label"]), [], 10.5, 13.5, ActionTree.Action.Successful)

        self.__check_drawing(a, 400, "49633bf6bbc7396c801504e3de64ff2e")

    def test_one_successful_action(self):
        a = self.__create_mocked_action("a", "label", [], 10.5, 13.5, ActionTree.Action.Successful)

        self.__check_drawing(a, 200, "0d141dc36bd75e0a326981afbb60bd32")

    def test_one_failed_action(self):
        a = self.__create_mocked_action("a", "label", [], 10.5, 13.5, ActionTree.Action.Failed)

        self.__check_drawing(a, 200, "7a4ab05cce5a6481d39624b0be845a77")

    def test_one_canceled_action(self):
        a = self.__create_mocked_action("a", "label", [], 10.5, 13.5, ActionTree.Action.Canceled)

        self.__check_drawing(a, 200, "04dfd9439857807e91f149379c197586")

    def test_two_chained_actions(self):
        a1 = self.__create_mocked_action("a1", "a1", [], 10.5, 13.5, ActionTree.Action.Successful)
        a2 = self.__create_mocked_action("a2", "a2", [a1], 14.0, 15.5, ActionTree.Action.Successful)

        self.__check_drawing(a2, 200, "0c61091279a919b19a6a9c70f7c18bf7")

    def test_action_with_two_dependencies(self):
        a1 = self.__create_mocked_action("a1", "a1", [], 10.5, 13.5, ActionTree.Action.Successful)
        a2 = self.__create_mocked_action("a2", "a2", [], 11.5, 14.0, ActionTree.Action.Successful)
        a3 = self.__create_mocked_action("a3", "a3", [a1, a2], 14.0, 15.5, ActionTree.Action.Successful)

        self.__check_drawing(a3, 200, "18dbd9c8afc79f7a1a6f211c35a4e919")

    def test_action_with_two_dependents(self):
        a1 = self.__create_mocked_action("a1", "a1", [], 12.5, 13.5, ActionTree.Action.Successful)
        a2 = self.__create_mocked_action("a2", "a2", [a1], 15.0, 16.5, ActionTree.Action.Successful)
        a3 = self.__create_mocked_action("a3", "a3", [a1], 14.0, 15.5, ActionTree.Action.Successful)
        a4 = self.__create_mocked_action("a4", "a4", [a2, a3], 17.0, 17.5, ActionTree.Action.Successful)

        self.__check_drawing(a4, 200, "e674fc65f495622102995619f4c2c1ed", "962c7cc9360019320895399bb15b23df")
