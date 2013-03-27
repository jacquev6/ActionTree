# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import os
import errno
import subprocess

from .Action import Action


class CreateDirectory(Action):
    def __init__(self, name):
        self.__name = name
        Action.__init__(self, self.__create, "mkdir " + self.__name)

    def __create(self):
        try:
            os.makedirs(self.__name)
        except OSError as e:
            if e.errno != errno.EEXIST or not os.path.isdir(self.__name):
                raise


class CallSubprocess(Action):
    def __init__(self, *args, **kwds):
        self.__args = list(args)
        self.__kwds = kwds
        Action.__init__(self, self.__call, " ".join(args))

    def __call(self):
        subprocess.check_call(self.__args, **self.__kwds)


class DeleteFile(Action):
    def __init__(self, name):
        self.__name = name
        Action.__init__(self, self.__delete, "rm " + self.__name)

    def __delete(self):
        try:
            os.unlink(self.__name)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

### todo TouchFile CopyFile
