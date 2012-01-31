import unittest
import time
from MockMockMock import Mock

from ActionTree import Action

class ExecuteMock:
    def __init__( self, mock ):
        self.__mock = mock

    def __call__( self ):
        self.__mock.begin()
        time.sleep( 0.1 )
        self.__mock.end()

class SingleThread( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.a = Mock( "a" )
        self.b = Mock( "b", self.a )
        self.aAction = Action( ExecuteMock( self.a.object ) )
        self.bAction = Action( ExecuteMock( self.b.object ) )

    def tearDown( self ):
        self.a.tearDown()

    def testSingleAction( self ):
        self.a.expect.begin()
        self.a.expect.end()

        self.aAction.execute()

    def testOneDependency( self ):
        self.aAction.addDependency( self.bAction )

        self.b.expect.begin()
        self.b.expect.end()
        self.a.expect.begin()
        self.a.expect.end()

        self.aAction.execute()

unittest.main()
