class Action:
    def __init__( self, execute ):
        self.__execute = execute
        self.__dependencies = set()

    def execute( self, threads = 1 ):
        self.__executeDependencies()
        self.__execute()

    def addDependency( self, dependency ):
        self.__dependencies.add( dependency )

    def __executeDependencies( self ):
        for dependency in self.__dependencies:
            dependency.execute()
