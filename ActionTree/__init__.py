# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import concurrent.futures as futures
import datetime
import multiprocessing


def execute(action, jobs=1, keep_going=False):
    """
    Recursively execute an action's dependencies then the action.

    :param int jobs: number of actions to execute in parallel
    :param bool keep_going: if True, then execution does not stop on first failure,
        but executes as many dependencies as possible.

    :raises CompoundException: when dependencies raise exceptions.
    """
    # @todo Return an ExecutionReport
    if jobs <= 0 or jobs is None:
        jobs = multiprocessing.cpu_count() + 1
    action._reset_before_execution()
    Executor(jobs, keep_going).execute(action)


class Executor(object):
    def __init__(self, jobs, keep_going):
        self.__jobs = jobs
        self.__keep_going = keep_going

    class Execution:
        # An aggregate for things that cannot be stored in Executor
        # (to allow several parallel calls to Executor.execute)
        def __init__(self, executor, to_be_submitted):
            self.executor = executor
            self.to_be_submitted = to_be_submitted
            self.submitted = dict()  # Future -> Action
            self.exceptions = []

    def execute(self, action):
        # Threads in pool just call self.__time_execute, which has no side effects.
        # To avoid races, only the thread calling Executor.execute is allowed to modify anything.

        with futures.ThreadPoolExecutor(max_workers=self.__jobs) as executor:
            execution = Executor.Execution(executor, set(action.get_all_dependencies()))
            while execution.to_be_submitted or execution.submitted:
                self.__progress(execution)

        if execution.exceptions:
            raise CompoundException(execution.exceptions)

    def __progress(self, execution):
        if self.__keep_going or not execution.exceptions:
            self.__submit(execution)
        else:
            self.__cancel(execution)
        self.__wait(execution)

    def __submit(self, execution):
        for action in set(execution.to_be_submitted):
            if all(d.status == Action.Successful for d in action.dependencies):
                execution.submitted[execution.executor.submit(self.__time_execute, action)] = action
                execution.to_be_submitted.remove(action)
            elif any(d.status in [Action.Failed, Action.Canceled] for d in action.dependencies):
                self.__mark_action_canceled(action)
                execution.to_be_submitted.remove(action)

    @staticmethod
    def __time_execute(action):
        exception = None
        try:
            begin_time = datetime.datetime.now()
            action.do_execute()
        except Exception as e:
            exception = e
        end_time = datetime.datetime.now()
        return (exception, begin_time, end_time)

    def __cancel(self, execution):
        for (f, action) in execution.submitted.items():
            if f.cancel():
                self.__mark_action_canceled(action)
                del execution.submitted[f]
        for action in execution.to_be_submitted:
            self.__mark_action_canceled(action)
        execution.to_be_submitted.clear()

    def __wait(self, execution):
        waited = futures.wait(execution.submitted.keys(), return_when=futures.FIRST_COMPLETED)
        for f in waited.done:
            action = execution.submitted[f]
            del execution.submitted[f]
            (exception, begin_time, end_time) = f.result()
            if exception:
                self.__mark_action_failed(action, begin_time, end_time)
                execution.exceptions.append(exception)
            else:
                self.__mark_action_successful(action, begin_time, end_time)

    @staticmethod
    def __mark_action_canceled(action):
        action._Action__status = Action.Canceled
        action._Action__begin_time = action._Action__end_time = datetime.datetime.now()

    @staticmethod
    def __mark_action_successful(action, begin_time, end_time):
        action._Action__status = Action.Successful
        action._Action__begin_time = begin_time
        action._Action__end_time = end_time

    @staticmethod
    def __mark_action_failed(action, begin_time, end_time):
        action._Action__status = Action.Failed
        action._Action__begin_time = begin_time
        action._Action__end_time = end_time


class Action(object):
    """
    The main class of ActionTree.
    An action to be started after all its dependencies are finished.

    This is a base class for your custom actions.
    You must define a ``def do_execute(self):`` method that performs the action.
    Its return value is ignored.
    If it raises and exception, it is captured and re-raised in a :exc:`CompoundException`

    See also :class:`.ActionFromCallable` if you just want to create an action from a simple callable.
    """
    # @todo Add a note about printing anything in do_execute
    # @todo Add a note saying

    def __init__(self, label):
        """
        :param label: whatever you want to attach to the action.
            Can be retrieved by :attr:`label` and :meth:`get_preview`.
        """
        self.__label = label
        self.__dependencies = set()
        self.__status = Action.Pending
        self.__begin_time = None
        self.__end_time = None

    @property
    def status(self):
        """
        The status of the action.

        Possible values: :attr:`Pending`, :attr:`Successful`, :attr:`Failed`, :attr:`Canceled`.
        """
        return self.__status

    Pending = 0
    "The initial :attr:`status`."
    Successful = 1
    "The :attr:`status` after a successful execution."
    Canceled = 2
    "The :attr:`status` after a failed execution where a dependency raised an exception."
    Failed = 3
    "The :attr:`status` after a failed execution where this action raised an exception."
    __Executing = 4

    @property
    def begin_time(self):
        """
        The local :class:`~datetime.datetime` at the begining of the execution of this action.
        """
        return self.__begin_time

    @property
    def end_time(self):
        """
        The local :class:`~datetime.datetime` at the end of the execution of this action.
        """
        return self.__end_time

    @property
    def label(self):
        """
        The label passed to the constructor.
        """
        return self.__label

    def add_dependency(self, dependency):
        """
        Add a dependency to be executed before this action.
        Order of insertion of dependencies is not important.

        :param Action dependency:

        :raises DependencyCycleException: when adding the new dependency would create a cycle.
        """
        if self in dependency.get_all_dependencies():
            raise DependencyCycleException()
        self.__dependencies.add(dependency)

    @property
    def dependencies(self):
        """
        Return the list of this action's dependencies.
        """
        return list(self.__dependencies)

    def get_all_dependencies(self):
        """
        Return the set of this action's recursive dependencies, including itself.
        """
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.get_all_dependencies()
        return dependencies

    def get_preview(self):
        """
        Return the labels of this action and its dependencies, in an order that could be the execution order.
        """
        return [action.__label for action in self.__get_possible_execution_order() if action.__label is not None]

    def __get_possible_execution_order(self, seen_actions=set()):
        actions = []
        if self not in seen_actions:
            seen_actions.add(self)
            for dependency in self.__dependencies:
                actions += dependency.__get_possible_execution_order(seen_actions)
            actions.append(self)
        return actions

    # @todo Remove default arguments
    def execute(self, jobs=1, keep_going=False):
        return execute(self, jobs, keep_going)

    def _reset_before_execution(self):
        self.__status = Action.Pending
        for dependency in self.__dependencies:
            dependency._reset_before_execution()


class ActionFromCallable(Action):
    """
    An :class:`.Action` sub-class for the simple use-case of using a plain callable as an action.
    """

    def __init__(self, do_execute, label):
        """
        :param label: see :class:`.Action`
        :param callable do_execute: the function to execute the action
        """
        super(ActionFromCallable, self).__init__(label)
        self.__do_execute = do_execute

    def do_execute(self):
        self.__do_execute()


class CompoundException(Exception):
    """
    Exception thrown by :meth:`.Action.execute` when a dependencies raise exceptions.
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
