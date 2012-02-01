class Action:
    def __init__( self, execute ):
        self.__execute = execute
        self.__dependencies = set()
        self.__executed = False

    def execute( self, threads = 1 ):
        if not self.__executed:
            self.__executeDependencies()
            self.__execute()
            self.__executed = True

    def addDependency( self, dependency ):
        self.__dependencies.add( dependency )

    def __executeDependencies( self ):
        for dependency in self.__dependencies:
            dependency.execute()
