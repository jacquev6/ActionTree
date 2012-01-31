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

class SingleAction( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "a" )
        self.action = Action( ExecuteMock( self.mock.object ) )

    def tearDown( self ):
        self.mock.tearDown()

    def test( self ):
        self.mock.expect.begin()
        self.mock.expect.end()

        self.action.execute()

unittest.main()
