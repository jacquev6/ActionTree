# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import threading

class Action:
    class Exception( Exception ):
        def __init__( self, exceptions ):
            self.exceptions = exceptions

    def __init__( self, execute, label ):
        self.__execute = execute
        self.__label = label
        self.__dependencies = set()
        self.__executed = False
        self.__failed = False
        self.__canceled = False
        self.__executing = False

    def addDependency( self, dependency ):
        if self in dependency.__getAllDependencies():
            raise Exception( "Dependency cycle" )
        self.__dependencies.add( dependency )

    def __getAllDependencies( self ):
        dependencies = set( [ self ] )
        for dependency in self.__dependencies:
            dependencies |= dependency.__getAllDependencies()
        return dependencies

    def execute( self, jobs = 1, keepGoing = False ):
        self.__resetBeforeExecution()
        self.__doExecute( jobs, keepGoing )

    def __resetBeforeExecution( self ):
        self.__executed = False
        self.__failed = False
        self.__canceled = False
        self.__executing = False
        for dependency in self.__dependencies:
            dependency.__resetBeforeExecution()

    def __doExecute( self, jobs, keepGoing ):
        condition = threading.Condition()
        exceptions = []
        threads = []
        for i in range( jobs ):
            thread = threading.Thread( target = self.__executeInOneThread, args = ( condition, exceptions, keepGoing ) )
            thread.start()
            threads.append( thread )
        for thread in threads:
            thread.join()
        if len( exceptions ) > 0:
            raise Action.Exception( exceptions )

    def __executeInOneThread( self, condition, exceptions, keepGoing ):
        while not self.__isFinished():
            self.__executeOneAction( condition, exceptions, keepGoing )

    def __executeOneAction( self, condition, exceptions, keepGoing ):
        with condition:
            action = self.__waitForActionToExecuteNow( condition )
            if action is None:
                return
            goOn = self.__prepareExecution( action )
        if goOn:
            try:
                action.__execute()
            except Exception, e:
                with condition:
                    action.__failed = True
                    exceptions.append( e )
                    if not keepGoing:
                        self.__canceled = True
            with condition:
                if not action.__failed:
                    action.__executed = True
                action.__executing = False
                condition.notifyAll()

    def __waitForActionToExecuteNow( self, condition ):
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
    def __getActionToExecuteNow( self ):
        if self.__executing or self.__isFinished():
            return None
        for dependency in self.__dependencies:
            action = dependency.__getActionToExecuteNow()
            if action is not None:
                return action
        if all( dependency.__isFinished() for dependency in self.__dependencies ):
            return self
        else:
            return None

    def __prepareExecution( self, action ):
        if any( d.__isFailure() for d in action.__dependencies ):
            action.__canceled = True
            return False
        else:
            action.__executing = True
            return True

    def __isFinished( self ):
        return self.__executed or self.__isFailure()

    def __isFailure( self ):
        return self.__canceled or self.__failed
