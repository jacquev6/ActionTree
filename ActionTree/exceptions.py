# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>


class CompoundException(Exception):
    """
    Exception thrown by :meth:`.Action.execute` when a dependeny raises an exception.
    """

    def __init__(self, exceptions):
        super(CompoundException, self).__init__(exceptions)
        self.__exceptions = exceptions

    @property
    def exceptions(self):
        """
        The list of the encapsulated exceptions.
        """
        return self.__exceptions


class DependencyCycleException(Exception):
    """
    Exception thrown by :meth:`.Action.add_dependency` when adding the new dependency would create a cycle.
    """

    def __init__(self):
        super(DependencyCycleException, self).__init__("Dependency cycle")
