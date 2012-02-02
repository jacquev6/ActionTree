import threading

class Action:
    def __init__( self, execute ):
        self.__execute = execute
        self.__dependencies = set()
        self.__executed = False
        self.__executing = False

    def execute( self, threads = 1 ):
        self.__condition = threading.Condition()
        threads = [ threading.Thread( target = self.__executeInOneThread ) for i in range( threads ) ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def __executeInOneThread( self ):
        while True:
            with self.__condition:
                a = None
                while a is None:
                    a = self.__getNextActionToExecute()
                    if self.__executed:
                        return
                    if a is None:
                        self.__condition.wait()
                a.__executing = True
            a.__execute()
            with self.__condition:
                a.__executed = True
                a.__executing = False
                self.__condition.notifyAll()

    def __getNextActionToExecute( self ):
        if self.__executed or self.__executing:
            return None
        for dependency in self.__dependencies:
            a = dependency.__getNextActionToExecute()
            if a is not None:
                return a
        if all( dependency.__executed for dependency in self.__dependencies ):
            return self
        else:
            return None

    def addDependency( self, dependency ):
        self.__dependencies.add( dependency )

    def __executeDependencies( self ):
        for dependency in self.__dependencies:
            dependency.execute()
