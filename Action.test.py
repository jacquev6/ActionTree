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
        self.mock = dict()
        self.action = dict()
        for name in "abcdef":
            self.addMock( name )

    def addMock( self, name ):
        if len( self.mock ) != 0:
            m = Mock( name, self.mock.values()[ 0 ] )
        else:
            m = Mock( name )
        a = Action( ExecuteMock( m.object ) )
        self.mock[ name ] = m
        self.action[ name ] = a

    def tearDown( self ):
        for mock in self.mock.itervalues():
            mock.tearDown()

    def addDependency( self, a, b ):
        self.action[ a ].addDependency( self.action[ b ] )

    def expectAction( self, name ):
        with self.mock[ name ].atomic:
            self.mock[ name ].expect.begin()
            self.mock[ name ].expect.end()

    def executeAction( self, name ):
        self.action[ name ].execute()

    def testSingleAction( self ):
        self.expectAction( "a" )

        self.executeAction( "a" )

    def testOneDependency( self ):
        self.addDependency( "a", "b" )

        self.expectAction( "b" )
        self.expectAction( "a" )

        self.executeAction( "a" )

    def testManyDependencies( self ):
        for name in "bcdef":
            self.addDependency( "a", name )

        with self.mock.values()[ 0 ].unordered:
            for name in "befcd":
                self.expectAction( name )
        self.expectAction( "a" )

        self.executeAction( "a" )

unittest.main()
