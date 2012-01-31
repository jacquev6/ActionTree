import unittest
import time
from MockMockMock import Mock

from ActionTree import Action

class SimpleExecution( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "a" )

    def tearDown( self ):
        self.mock.tearDown()

    def test( self ):
        self.mock.expect()
        Action( self.mock.object ).execute()

unittest.main()
