# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

"""
Stock actions are predefined common tasks (manipulating the filesystem, calling an external program, etc.)
They all specialize :class:`.Action`.
"""

from __future__ import division, absolute_import, print_function

import errno
import os
import shutil
import subprocess
import time


from . import Action


DEFAULT = object()


class NullAction(Action):
    """
    A stock action that does nothing.
    Useful as a placeholder for several dependencies.
    """
    def __init__(self, label=None, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, label, *args, **kwds)

    def do_execute(self, dependency_statuses):
        pass


class CallSubprocess(Action):
    """
    A stock action that calls a subprocess.

    Note: if the process fails,
    :func:`~subprocess.check_call` raises a :exc:`subprocess.CalledProcessError`,
    which `cannot be pickled <http://bugs.python.org/issue1692335>`__ in Python 2.
    So, in that case, this action catches the original exception and
    raises a :exc:`CalledProcessError`.
    """
    def __init__(self, command, kwargs={}, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, " ".join(command) if label is DEFAULT else label, *args, **kwds)
        self.__command = command
        self.__kwargs = kwargs

    def do_execute(self, dependency_statuses):
        # subprocess.CalledProcessError can't be pickled in Python2
        # See http://bugs.python.org/issue1692335
        try:
            subprocess.check_call(self.__command, **self.__kwargs)
        except subprocess.CalledProcessError as e:  # Not doctested: implementation detail
            raise CalledProcessError(e.returncode, e.cmd, e.output)


class CalledProcessError(Exception):
    """
    Raised by :class:`CallSubprocess`
    """


class CreateDirectory(Action):
    """
    A stock action that creates a directory.
    No error will be raised if the directory already exists.
    If the directory to create is nested, intermediate directories will be created as well.

    :param str name: the directory to create, passed to :func:`os.makedirs`.
    """
    def __init__(self, name, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "mkdir {}".format(name) if label is DEFAULT else label, *args, **kwds)
        self.__name = name

    def do_execute(self, dependency_statuses):
        try:
            os.makedirs(self.__name)
        except OSError as e:  # Not doctested: implementation detail
            if e.errno != errno.EEXIST or not os.path.isdir(self.__name):
                raise


class DeleteFile(Action):  # Not doctested: could be
    """
    A stock action that deletes a file.
    No error will be raise if the file doesn't exist.

    :param str name: the name of the file to delete, passed to :func:`os.unlink`.
    """
    def __init__(self, name, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "rm {}".format(name) if label is DEFAULT else label, *args, **kwds)
        self.__name = name

    def do_execute(self, dependency_statuses):
        try:
            os.unlink(self.__name)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


class DeleteDirectory(Action):  # Not doctested: could be
    """
    A stock action that deletes a directory (recursively).
    No error will be raise if the directory doesn't exist.

    :param str name: the name of the directory to delete, passed to :func:`shutil.rmtree`.
    """
    def __init__(self, name, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "rm -r {}".format(name) if label is DEFAULT else label, *args, **kwds)
        self.__name = name

    def do_execute(self, dependency_statuses):
        try:
            shutil.rmtree(self.__name)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


class CopyFile(Action):  # Not doctested: could be
    """
    A stock action that copies a file. Arguments are passed to :func:`shutil.copy`.

    :param str src: the file to copy
    :param str dst: the destination
    """
    def __init__(self, src, dst, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "cp {} {}".format(src, dst) if label is DEFAULT else label, *args, **kwds)
        self.__src = src
        self.__dst = dst

    def do_execute(self, dependency_statuses):
        shutil.copy(self.__src, self.__dst)


class TouchFile(Action):  # Not doctested: could be
    """
    A stock action that touches a file.
    If the file already exists, its modification time will be modified.
    Else, it will be created, empty.

    Note that the containing directory must exist.
    You might want to ensure that by adding a :class:`CreateDirectory` as a dependency.

    :param str name: the name of the file to touch. Passed to :func:`open` and/or :func:`os.utime`.
    """

    def __init__(self, name, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "touch {}".format(name) if label is DEFAULT else label, *args, **kwds)
        self.__name = name

    def do_execute(self, dependency_statuses):
        open(self.__name, "ab").close()  # Create the file if needed
        os.utime(self.__name, None)  # Actually change its time


class Sleep(Action):
    """
    A stock action that sleeps for a certain duration.

    :param float secs: seconds to sleep, passed to :func:`time.sleep`.
    """
    def __init__(self, secs, label=DEFAULT, *args, **kwds):
        """
        @todoc
        """
        Action.__init__(self, "sleep {}".format(secs) if label is DEFAULT else label, *args, **kwds)
        self.__secs = secs

    def do_execute(self, dependency_statuses):
        time.sleep(self.__secs)
