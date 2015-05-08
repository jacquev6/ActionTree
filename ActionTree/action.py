# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import multiprocessing
import threading
import time

from .exceptions import CompoundException, DependencyCycleException


class Action:
    """
    The main class of ActionTree.
    An action to be started after all its dependencies are finished.
    """

    _time = time.time  # Allow static dependency injection. But keep it private.

    def __init__(self, execute, label):
        """
        :param callable execute: the function to execute the action
        :param label: whatever you want to attach to the action. Can be retrieved by :attr:`label` and :meth:`get_preview`.
        """
        self.__execute = execute
        self.__label = label
        self.__dependencies = set()
        self.__status = Action.Pending

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
    "The :attr:`status` after a failed execution whre this action raised an exception."
    __Executing = 4

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
        """
        if self in dependency.__get_all_dependencies():
            raise DependencyCycleException()
        self.__dependencies.add(dependency)

    def get_dependencies(self):
        """
        Return the list of this action's dependencies.
        """
        return list(self.__dependencies)

    def __get_all_dependencies(self):
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.__get_all_dependencies()
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

    def execute(self, jobs=1, keep_going=False):
        """
        Recursively execute this action's dependencies then this action.

        If dependencies raise exceptions, these exceptions are encapsulated in a :exc:`.CompoundException` and thrown.

        :param int jobs: number of actions to execute in parallel
        :param bool keep_going: if True, then execution does not stop on first failure, but executes as many dependencies as possible.
        """
        if jobs <= 0:
            jobs = multiprocessing.cpu_count() + 1
        self.__reset_before_execution()
        self.__do_execute(jobs, keep_going)

    def __reset_before_execution(self):
        self.__status = Action.Pending
        for dependency in self.__dependencies:
            dependency.__reset_before_execution()

    def __do_execute(self, jobs, keep_going):
        condition = threading.Condition()
        exceptions = []
        threads = []
        for i in range(jobs):
            thread = threading.Thread(target=self.__execute_in_one_thread, args=(condition, exceptions, keep_going))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        if len(exceptions) > 0:
            self.__mark_canceled_actions()
            raise CompoundException(exceptions)

    def __execute_in_one_thread(self, condition, exceptions, keep_going):
        while not self.__is_finished():
            self.__execute_one_action(condition, exceptions, keep_going)

    def __execute_one_action(self, condition, exceptions, keep_going):
        with condition:
            action = self.__wait_for_action_to_execute_now(condition)
            if action is None:
                return
            go_on = self.__prepare_execution(action)
        if go_on:
            action.begin_time = Action._time()
            try:
                action.__execute()
            except Exception as e:
                with condition:
                    action.__status = Action.Failed
                    exceptions.append(e)
                    if not keep_going and action is not self:
                        self.__cancel_action(self)
            finally:
                action.end_time = Action._time()
            with condition:
                if action.__status != Action.Failed:
                    action.__status = Action.Successful
                condition.notify_all()

    def __wait_for_action_to_execute_now(self, condition):
        action = None
        while action is None:
            action = self.__get_action_to_execute_now()
            if self.__is_finished():
                return None
            if action is None:
                condition.wait()
        return action

    ### Returns None in two cases:
    ###  - when self is finished or failed
    ###  - when nothing can be started yet, because dependencies are still being executed
    def __get_action_to_execute_now(self):
        if self.__status == Action.__Executing or self.__is_finished():
            return None
        for dependency in self.__dependencies:
            action = dependency.__get_action_to_execute_now()
            if action is not None:
                return action
        if all(dependency.__is_finished() for dependency in self.__dependencies):
            return self
        else:
            return None

    def __prepare_execution(self, action):
        if any(d.__is_failure() for d in action.__dependencies):
            self.__cancel_action(action)
            return False
        else:
            action.__status = Action.__Executing
            return True

    def __mark_canceled_actions(self):
        for dependency in self.__dependencies:
            dependency.__mark_canceled_actions()
        if not self.__is_finished():
            self.__cancel_action(self)

    def __cancel_action(self, action):
        action.__status = Action.Canceled
        action.begin_time = Action._time()
        action.end_time = action.begin_time

    def __is_finished(self):
        return self.__status in [Action.Successful, Action.Failed, Action.Canceled]

    def __is_failure(self):
        return self.__status in [Action.Failed, Action.Canceled]
