# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import time

from .Action import Action


class TimedAction(Action):
    """
    Foo
    """
    time = time.time  # Allow static dependency injection

    def __init__(self, execute, label):
        self.__execute = execute
        Action.__init__(self, self.__timedExecute, label)

    def __timedExecute(self):
        self.beginTime = self.time()
        try:
            self.__execute()
        finally:
            self.endTime = self.time()
