import unittest
import threading
import time
from MockMockMock import Mock

from ActionTree import Action

class ExecuteMock:
    def __init__( self, mock ):
        self.__mock = mock
        self.__lock = threading.Lock()

    def __call__( self ):
        with self.__lock:
            self.__mock.begin()
        time.sleep( 0.1 )
        with self.__lock:
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
        a = Action( m.object )
        self.mock[ name ] = m
        self.action[ name ] = a

    def tearDown( self ):
        for mock in self.mock.itervalues():
            mock.tearDown()

    def addDependency( self, a, b ):
        self.action[ a ].addDependency( self.action[ b ] )

    def expectAction( self, name ):
        self.mock[ name ].expect()

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

    def testDeepDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "b", "c" )
        self.addDependency( "c", "d" )
        self.addDependency( "d", "e" )
        self.addDependency( "e", "f" )

        self.expectAction( "f" )
        self.expectAction( "e" )
        self.expectAction( "d" )
        self.expectAction( "c" )
        self.expectAction( "b" )
        self.expectAction( "a" )

        self.executeAction( "a" )

    def testDiamondDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "a", "c" )
        self.addDependency( "b", "d" )
        self.addDependency( "c", "d" )

        self.expectAction( "d" )
        with self.mock.values()[ 0 ].unordered:
            self.expectAction( "b" )
            self.expectAction( "c" )
        self.expectAction( "a" )

        self.executeAction( "a" )

class ThreadPool( unittest.TestCase ):
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

    def expectBegin( self, name ):
        self.mock[ name ].expect.begin()

    def expectEnd( self, name ):
        self.mock[ name ].expect.end()

    def executeAction( self, name ):
        self.action[ name ].execute( threads = 3 )

    def testSingleAction( self ):
        self.expectBegin( "a" )
        self.expectEnd( "a" )

        self.executeAction( "a" )

    def testManyDependencies( self ):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency( "a", name )

        with self.mock.values()[ 0 ].unordered:
            for name in dependencies:
                self.expectBegin( name )
        with self.mock.values()[ 0 ].unordered:
            for name in dependencies:
                self.expectEnd( name )
        self.expectBegin( "a" )
        self.expectEnd( "a" )

        self.executeAction( "a" )

    def testDiamondDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "a", "c" )
        self.addDependency( "b", "d" )
        self.addDependency( "c", "d" )

        self.expectBegin( "d" )
        self.expectEnd( "d" )
        with self.mock.values()[ 0 ].unordered:
            self.expectBegin( "b" )
            self.expectBegin( "c" )
        with self.mock.values()[ 0 ].unordered:
            self.expectEnd( "b" )
            self.expectEnd( "c" )
        self.expectBegin( "a" )
        self.expectEnd( "a" )

        self.executeAction( "a" )

    def testDeepDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "b", "c" )
        self.addDependency( "c", "d" )
        self.addDependency( "d", "e" )
        self.addDependency( "e", "f" )

        self.expectBegin( "f" )
        self.expectEnd( "f" )
        self.expectBegin( "e" )
        self.expectEnd( "e" )
        self.expectBegin( "d" )
        self.expectEnd( "d" )
        self.expectBegin( "c" )
        self.expectEnd( "c" )
        self.expectBegin( "b" )
        self.expectEnd( "b" )
        self.expectBegin( "a" )
        self.expectEnd( "a" )

        self.executeAction( "a" )

unittest.main()
