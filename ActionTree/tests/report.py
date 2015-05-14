# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import collections
import unittest

import ActionTree
from ActionTree.drawings import *


MockAction = collections.namedtuple("MockAction", "label, dependencies, begin_time, end_time, status")

successful = ActionTree.Action.Successful
failed = ActionTree.Action.Failed
canceled = ActionTree.Action.Canceled
