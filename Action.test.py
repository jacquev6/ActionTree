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

class TestCase( object ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.__mock = dict()
        self.__action = dict()
        for name in "abcdef":
            self.__addMock( name )

    def __addMock( self, name ):
        if len( self.__mock ) != 0:
            m = Mock( name, self.__mock.values()[ 0 ] )
        else:
            m = Mock( name )
        a = Action( self.callableFromMock( m.object ) )
        self.__mock[ name ] = m
        self.__action[ name ] = a

    def tearDown( self ):
        for mock in self.__mock.itervalues():
            mock.tearDown()

    def __addDependency( self, a, b ):
        self.__action[ a ].addDependency( self.__action[ b ] )

    def getMock( self, name ):
        return self.__mock[ name ]

    def __executeAction( self, name ):
        self.executeAction( self.__action[ name ] )

    @property
    def unordered( self ):
        return self.__mock.values()[ 0 ].unordered

    def testManyDependencies( self ):
        dependencies = "bcd"
        for name in dependencies:
            self.__addDependency( "a", name )

        self.expectManyDependencies( dependencies )

        self.__executeAction( "a" )

    def testDeepDependencies( self ):
        self.__addDependency( "a", "b" )
        self.__addDependency( "b", "c" )
        self.__addDependency( "c", "d" )
        self.__addDependency( "d", "e" )
        self.__addDependency( "e", "f" )

        self.expectDeepDependencies()

        self.__executeAction( "a" )

    def testDiamondDependencies( self ):
        self.__addDependency( "a", "b" )
        self.__addDependency( "a", "c" )
        self.__addDependency( "b", "d" )
        self.__addDependency( "c", "d" )

        self.expectDiamondDependencies()

        self.__executeAction( "a" )

class SingleThread( TestCase, unittest.TestCase ):
    def callableFromMock( self, m ):
        return m

    def executeAction( self, action ):
        action.execute()

    def __expectAction( self, name ):
        self.getMock( name ).expect()

    def expectManyDependencies( self, dependencies ):
        with self.unordered:
            for name in dependencies:
                self.__expectAction( name )
        self.__expectAction( "a" )

    def expectDeepDependencies( self ):
        self.__expectAction( "f" )
        self.__expectAction( "e" )
        self.__expectAction( "d" )
        self.__expectAction( "c" )
        self.__expectAction( "b" )
        self.__expectAction( "a" )

    def expectDiamondDependencies( self ):
        self.__expectAction( "d" )
        with self.unordered:
            self.__expectAction( "b" )
            self.__expectAction( "c" )
        self.__expectAction( "a" )

class ThreadPool( TestCase, unittest.TestCase ):
    def callableFromMock( self, m ):
        return ExecuteMock( m )

    def executeAction( self, action ):
        action.execute( threads = 3 )

    def __expectBegin( self, name ):
        self.getMock( name ).expect.begin()

    def __expectEnd( self, name ):
        self.getMock( name ).expect.end()

    def expectManyDependencies( self, dependencies ):
        with self.unordered:
            for name in dependencies:
                self.__expectBegin( name )
        with self.unordered:
            for name in dependencies:
                self.__expectEnd( name )
        self.__expectBegin( "a" )
        self.__expectEnd( "a" )

    def expectDiamondDependencies( self ):
        self.__expectBegin( "d" )
        self.__expectEnd( "d" )
        with self.unordered:
            self.__expectBegin( "b" )
            self.__expectBegin( "c" )
        with self.unordered:
            self.__expectEnd( "b" )
            self.__expectEnd( "c" )
        self.__expectBegin( "a" )
        self.__expectEnd( "a" )

    def expectDeepDependencies( self ):
        self.__expectBegin( "f" )
        self.__expectEnd( "f" )
        self.__expectBegin( "e" )
        self.__expectEnd( "e" )
        self.__expectBegin( "d" )
        self.__expectEnd( "d" )
        self.__expectBegin( "c" )
        self.__expectEnd( "c" )
        self.__expectBegin( "b" )
        self.__expectEnd( "b" )
        self.__expectBegin( "a" )
        self.__expectEnd( "a" )

unittest.main()
