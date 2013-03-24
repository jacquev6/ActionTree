# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.


class CompoundException(Exception):
    """
    An exception class thrown by :meth:`Action.execute` when a dependeny raises an exception.
    """

    def __init__(self, exceptions):
        self.__exceptions = exceptions

    @property
    def exceptions(self):
        """
        The list of the encapsulated exceptions
        """
        return self.__exceptions

    def __str__(self):
        return "CompoundException: [" + ", ".join(str(e) for e in self.__exceptions) + "]"
