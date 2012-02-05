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
        self.__dependencies.add( dependency )

    def execute( self, threads = 1, keepGoing = False ):
        self.__condition = threading.Condition()
        self.__exceptions = []
        self.__keepGoing = keepGoing
        threads = [ threading.Thread( target = self.__executeInOneThread ) for i in range( threads ) ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if len( self.__exceptions ) > 0:
            raise Action.Exception( self.__exceptions )

    def __executeInOneThread( self ):
        while True:
            with self.__condition:
                a = None
                while a is None:
                    a = self.__getNextActionToExecute()
                    if self.__executed or self.__canceled or self.__failed:
                        return
                    if a is None:
                        self.__condition.wait()
                if any( d.__failed or d.__canceled for d in a.__dependencies ):
                    a.__canceled = True
                else:
                    a.__executing = True
            if a.__executing:
                try:
                    a.__execute()
                except Exception, e:
                    with self.__condition:
                        a.__failed = True
                        self.__exceptions.append( e )
                        if not self.__keepGoing:
                            self.__canceled = True
                with self.__condition:
                    if not a.__failed:
                        a.__executed = True
                    a.__executing = False
                    self.__condition.notifyAll()

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
