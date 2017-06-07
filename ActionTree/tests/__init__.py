# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import unittest

try:
    import unittest.mock
except ImportError:
    import mock
    unittest.mock = mock
