import threading

class Action:
    class Exception( Exception ):
        def __init__( self, exceptions ):
            self.exceptions = exceptions

    def __init__( self, execute ):
        self.__execute = execute
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
        dependencies = [ self ]
        for dependency in self.__dependencies:
            dependencies += dependency.__getAllDependencies()
        return dependencies

    def execute( self, jobs = 1, keepGoing = False ):
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
        while True:
            with condition:
                action = None
                while action is None:
                    action = self.__getActionToExecuteNow()
                    if self.__isFinished():
                        return
                    if action is None:
                        condition.wait()
                if any( d.__isFailure() for d in action.__dependencies ):
                    action.__canceled = True
                else:
                    action.__executing = True
            if action.__executing:
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

    def __isFinished( self ):
        return self.__executed or self.__isFailure()

    def __isFailure( self ):
        return self.__canceled or self.__failed
