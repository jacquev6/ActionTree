# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>


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
