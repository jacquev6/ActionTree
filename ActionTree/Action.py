# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import threading
import time

from .CompoundException import CompoundException


class Action:
    _time = time.time  # Allow static dependency injection. But keep it private.

    Pending = 0
    Successful = 1
    Canceled = 2
    Failed = 3
    __Executing = 4

    def __init__(self, execute, label):
        self.__execute = execute
        self.__label = label
        self.__dependencies = set()
        self.__status = Action.Pending

    @property
    def status(self):
        return self.__status

    def addDependency(self, dependency):
        if self in dependency.__getAllDependencies():
            raise Exception("Dependency cycle")
        self.__dependencies.add(dependency)

    def __getAllDependencies(self):
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.__getAllDependencies()
        return dependencies

    def getPreview(self):
        preview = []
        for dependency in self.__dependencies:
            preview += dependency.getPreview()
        preview.append(self.__label)
        return preview

    def execute(self, jobs=1, keepGoing=False):
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
            except Exception, e:
                with condition:
                    action.__status = Action.Failed
                    exceptions.append(e)
                    if not keepGoing and action is not self:
                        self.__status = Action.Canceled
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
            action.__status = Action.Canceled
            return False
        else:
            action.__status = Action.__Executing
            return True

    def __markCanceledActions(self):
        for dependency in self.__dependencies:
            dependency.__markCanceledActions()
        if not self.__isFinished():
            self.__status = Action.Canceled

    def __isFinished(self):
        return self.__status in [Action.Successful, Action.Failed, Action.Canceled]

    def __isFailure(self):
        return self.__status in [Action.Failed, Action.Canceled]
