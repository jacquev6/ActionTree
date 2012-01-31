class Action:
    def __init__( self, execute ):
        self.__execute = execute

    def execute( self ):
        self.__execute()
