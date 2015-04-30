# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import multiprocessing
import threading
import time

from .CompoundException import CompoundException


class Action:
    """
    The main class of ActionTree. It represents an action to be started after all its dependencies
    are finished.
    """

    _time = time.time  # Allow static dependency injection. But keep it private.

    Pending = 0
    Successful = 1
    Canceled = 2
    Failed = 3
    __Executing = 4

    def __init__(self, execute, label):
        """
        :param callable execute: the function to execute the action
        :param label: whatever you want to attach to the action. Can be retrieved by :attr:`Action.label` and :meth:`Action.getPreview`.
        """
        self.__execute = execute
        self.__label = label
        self.__dependencies = set()
        self.__status = Action.Pending

    @property
    def status(self):
        """
        The status of the action.

        Possible values:

        - :attr:`Action.Pending`, initially
        - :attr:`Action.Successful` after normal execution
        - :attr:`Action.Failed` if the execution raised an exception
        - :attr:`Action.Canceled` if some dependency raised an exception
        """
        return self.__status

    @property
    def label(self):
        """
        The label passed to the constructor
        """
        return self.__label

    def addDependency(self, dependency):
        """
        Adds a dependency to be executed before this action.
        Order of insertion of dependencies is not important.

        :param ``Action`` dependency:
        """
        if self in dependency.__getAllDependencies():
            raise Exception("Dependency cycle")
        self.__dependencies.add(dependency)

    def getDependencies(self):
        """
        Returns the list of this action's dependencies.
        """
        return list(self.__dependencies)

    def __getAllDependencies(self):
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.__getAllDependencies()
        return dependencies

    def getPreview(self):
        """
        Returns the labels of this action and its dependencies, in an order that could be the execution order.
        """
        return [action.__label for action in self.__getPossibleExecutionOrder() if action.__label is not None]

    def __getPossibleExecutionOrder(self, seenActions=set()):
        actions = []
        if self not in seenActions:
            seenActions.add(self)
            for dependency in self.__dependencies:
                actions += dependency.__getPossibleExecutionOrder(seenActions)
            actions.append(self)
        return actions

    def execute(self, jobs=1, keepGoing=False):
        """
        Recursively executes this action's dependencies then this action.

        If dependencies raise exceptions, these exceptions are encapsulated in a :class:`CompoundException` and this :class:`CompoundException` is thrown.

        :param int jobs: number of actions to execute in parallel
        :param bool keepGoing: if True, then :meth:`execute` does not stop on first failure, but executes as many dependencies as possible.
        """
        if jobs <= 0:
            jobs = multiprocessing.cpu_count() + 1
        self.__resetBeforeExecution()
        self.__doExecute(jobs, keepGoing)

    def __resetBeforeExecution(self):
        self.__status = Action.Pending
        for dependency in self.__dependencies:
            dependency.__resetBeforeExecution()

    def __doExecute(self, jobs, keepGoing):
        condition = threading.Condition()
        exceptions = []
        threads = []
        for i in range(jobs):
            thread = threading.Thread(target=self.__executeInOneThread, args=(condition, exceptions, keepGoing))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        if len(exceptions) > 0:
            self.__markCanceledActions()
            raise CompoundException(exceptions)

    def __executeInOneThread(self, condition, exceptions, keepGoing):
        while not self.__isFinished():
            self.__executeOneAction(condition, exceptions, keepGoing)

    def __executeOneAction(self, condition, exceptions, keepGoing):
        with condition:
            action = self.__waitForActionToExecuteNow(condition)
            if action is None:
                return
            goOn = self.__prepareExecution(action)
        if goOn:
            action.beginTime = Action._time()
            try:
                action.__execute()
            except Exception as e:
                with condition:
                    action.__status = Action.Failed
                    exceptions.append(e)
                    if not keepGoing and action is not self:
                        self.__cancelAction(self)
            finally:
                action.endTime = Action._time()
            with condition:
                if action.__status != Action.Failed:
                    action.__status = Action.Successful
                condition.notifyAll()

    def __waitForActionToExecuteNow(self, condition):
        action = None
        while action is None:
            action = self.__getActionToExecuteNow()
            if self.__isFinished():
                return None
            if action is None:
                condition.wait()
        return action

    ### Returns None in two cases:
    ###  - when self is finished or failed
    ###  - when nothing can be started yet, because dependencies are still being executed
    def __getActionToExecuteNow(self):
        if self.__status == Action.__Executing or self.__isFinished():
            return None
        for dependency in self.__dependencies:
            action = dependency.__getActionToExecuteNow()
            if action is not None:
                return action
        if all(dependency.__isFinished() for dependency in self.__dependencies):
            return self
        else:
            return None

    def __prepareExecution(self, action):
        if any(d.__isFailure() for d in action.__dependencies):
            self.__cancelAction(action)
            return False
        else:
            action.__status = Action.__Executing
            return True

    def __markCanceledActions(self):
        for dependency in self.__dependencies:
            dependency.__markCanceledActions()
        if not self.__isFinished():
            self.__cancelAction(self)

    def __cancelAction(self, action):
        action.__status = Action.Canceled
        action.beginTime = Action._time()
        action.endTime = action.beginTime

    def __isFinished(self):
        return self.__status in [Action.Successful, Action.Failed, Action.Canceled]

    def __isFailure(self):
        return self.__status in [Action.Failed, Action.Canceled]
