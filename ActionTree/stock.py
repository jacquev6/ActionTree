# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>
"""
Stock actions are predefined common tasks (manipulating the filesystem, calling an external program, etc.)
They all specialize :class:`.Action`.
"""

import errno
import os
import shutil
import subprocess
import time
from functools import partial

from .action import Action


class NullAction(Action):
    """
    A stock action that does nothing.
    Useful as a placeholder for several dependencies.
    """
    def __init__(self):
        Action.__init__(self, lambda: None, None)


class CallSubprocess(Action):
    """
    A stock action that calls a subprocess.

    Arguments are forwarded exactly to :func:`subprocess.check_call`.
    """
    def __init__(self, args, **kwds):
        self.__args = args
        self.__kwds = kwds
        Action.__init__(self, self.__call, " ".join(args))

    def __call(self):
        subprocess.check_call(self.__args, **self.__kwds)


class CreateDirectory(Action):
    """
    A stock action that creates a directory.
    No error will be raised if the directory already exists.
    If the directory to create is nested, intermediate directories will be created as well.

    :param str name: the directory to create, passed to :func:`os.makedirs`.
    """
    def __init__(self, name):
        self.__name = name
        Action.__init__(self, self.__create, "mkdir {}".format(name))

    def __create(self):
        try:
            os.makedirs(self.__name)
        except OSError as e:
            if e.errno != errno.EEXIST or not os.path.isdir(self.__name):
                raise


class DeleteFile(Action):
    """
    A stock action that deletes a file.
    No error will be raise if the file doesn't exist.

    :param str name: the name of the file to delete, passed to :func:`os.unlink`.
    """
    def __init__(self, name):
        self.__name = name
        Action.__init__(self, self.__delete, "rm {}".format(name))

    def __delete(self):
        try:
            os.unlink(self.__name)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


class CopyFile(Action):
    """
    A stock action that copies a file. Arguments are passed to :func:`shutil.copy`.

    :param str src: the file to copy
    :param str dst: the destination
    """
    def __init__(self, src, dst):
        self.__src = src
        self.__dst = dst
        Action.__init__(self, self.__copy, "cp {} {}".format(src, dst))

    def __copy(self):
        shutil.copy(self.__src, self.__dst)


class TouchFile(Action):
    """
    A stock action that touches a file.
    If the file already exists, its modification time will be modified.
    Else, it will be created, empty.

    Note that the containing directory must exist.
    You might want to ensure that by adding a :class:`CreateDirectory` as a dependency.

    :param str name: the name of the file to touch. Passed to :func:`open` and/or :func:`os.utime`.
    """

    _open = open  # Allow static dependency injection. But keep it private.

    def __init__(self, name):
        self.__name = name
        Action.__init__(self, self.__touch, "touch {}".format(name))

    def __touch(self):
        self._open(self.__name, "ab").close()  # Create the file if needed
        os.utime(self.__name, None)  # Actually change its time


class Sleep(Action):
    """
    A stock action that sleeps for a certain duration.

    :param float secs: seconds to sleep, passed to :func:`time.sleep`.
    """
    def __init__(self, secs):
        Action.__init__(self, partial(time.sleep, secs), "sleep {}".format(secs))
