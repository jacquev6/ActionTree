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

    def execute( self, threads = 1, keepGoing = False ):
        condition = threading.Condition()
        exceptions = []
        threads = [ threading.Thread( target = self.__executeInOneThread, args = ( condition, exceptions, keepGoing ) ) for i in range( threads ) ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if len( exceptions ) > 0:
            raise Action.Exception( exceptions )

    def __executeInOneThread( self, condition, exceptions, keepGoing ):
        while True:
            with condition:
                a = None
                while a is None:
                    a = self.__getNextActionToExecute()
                    if self.__executed or self.__canceled or self.__failed:
                        return
                    if a is None:
                        condition.wait()
                if any( d.__failed or d.__canceled for d in a.__dependencies ):
                    a.__canceled = True
                else:
                    a.__executing = True
            if a.__executing:
                try:
                    a.__execute()
                except Exception, e:
                    with condition:
                        a.__failed = True
                        exceptions.append( e )
                        if not keepGoing:
                            self.__canceled = True
                with condition:
                    if not a.__failed:
                        a.__executed = True
                    a.__executing = False
                    condition.notifyAll()

    def __getNextActionToExecute( self ):
        if self.__executed or self.__executing or self.__failed or self.__canceled:
            return None
        for dependency in self.__dependencies:
            a = dependency.__getNextActionToExecute()
            if a is not None:
                return a
        if all( dependency.__executed or dependency.__failed or dependency.__canceled for dependency in self.__dependencies ):
            return self
        else:
            return None
