# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import errno
import os
import shutil
import subprocess
import time

from .Action import Action


class Sleep(Action):
    def __init__(self, duration):
        Action.__init__(self, lambda: time.sleep(duration), "sleep " + str(duration))


class NullAction(Action):
    def __init__(self):
        Action.__init__(self, lambda: None, None)


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


class CopyFile(Action):
    def __init__(self, src, dst):
        self.__src = src
        self.__dst = dst
        Action.__init__(self, self.__copy, "cp " + self.__src + " " + self.__dst)

    def __copy(self):
        shutil.copy(self.__src, self.__dst)
        # time.sleep(1)  # Race condition ? Microsoft cl doesn't see the file when called just after the copy...


class TouchFiles(Action):
    _open = open  # Allow static dependency injection. But keep it private.

    def __init__(self, names):
        assert len(names) != 0
        self.__names = names
        Action.__init__(self, self.__touch, "touch " + " ".join(self.__names))

    def __touch(self):
        # time.sleep(1)  # Ensure file will be more recent than any other touched files
        for name in self.__names:
            self._open(name, "ab").close()  # Create the file if needed
            os.utime(name, None)  # Actually change its time
