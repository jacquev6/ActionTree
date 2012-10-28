import unittest
import threading
import time
import MockMockMock

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

class TestCase( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.__mockEngine = MockMockMock.Engine()
        self.__mock = dict()
        self.__action = dict()
        for name in "abcdef":
            self.__addMock( name )

    def __addMock( self, name ):
        m = self.__mockEngine.create( name )
        a = Action( self.callableFromMock( m.object ), name )
        self.__mock[ name ] = m
        self.__action[ name ] = a

    def tearDown( self ):
        self.__mockEngine.tearDown()

    def addDependency( self, a, b ):
        self.__action[ a ].addDependency( self.__action[ b ] )

    def getMock( self, name ):
        return self.__mock[ name ]

    def getAction( self, name ):
        return self.__action[ name ]

    @property
    def unordered( self ):
        return self.__mockEngine.unordered

    @property
    def optional( self ):
        return self.__mockEngine.optional

class ThreadingTestCase:
    def testManyDependencies( self ):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency( "a", name )

        self.expectManyDependencies( dependencies )

        self.executeAction( self.getAction( "a" ) )

    def testDeepDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "b", "c" )
        self.addDependency( "c", "d" )
        self.addDependency( "d", "e" )
        self.addDependency( "e", "f" )

        self.expectDeepDependencies()

        self.executeAction( self.getAction( "a" ) )

    def testDiamondDependencies( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "a", "c" )
        self.addDependency( "b", "d" )
        self.addDependency( "c", "d" )

        self.expectDiamondDependencies()

        self.executeAction( self.getAction( "a" ) )

class SingleThread( TestCase, ThreadingTestCase ):
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

class ThreadPool( TestCase, ThreadingTestCase ):
    def callableFromMock( self, m ):
        return ExecuteMock( m )

    def executeAction( self, action ):
        action.execute( jobs = 3 )

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

class ExceptionsHandling( TestCase ):
    def callableFromMock( self, m ):
        return m

    def testExceptionInDependency( self ):
        dependencies = "b"
        for name in dependencies:
            self.addDependency( "a", name )

        e = Exception()
        self.getMock( "b" ).expect().andRaise( e )

        with self.assertRaises( Action.Exception ) as cm:
            self.getAction( "a" ).execute()
        self.assertEqual( len( cm.exception.exceptions ), 1 )
        self.assertIs( cm.exception.exceptions[ 0 ], e )

    def testExceptionsInDependencies_KeepGoing( self ):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency( "a", name )

        eb = Exception()
        ec = Exception()
        with self.unordered:
            self.getMock( "b" ).expect().andRaise( eb )
            self.getMock( "c" ).expect().andRaise( ec )
            self.getMock( "d" ).expect()

        with self.assertRaises( Action.Exception ) as cm:
            self.getAction( "a" ).execute( keepGoing = True )
        self.assertEqual( len( cm.exception.exceptions ), 2 )

    def testExceptionsInDependencies_NoKeepGoing( self ):
        dependencies = "bcd"
        for name in dependencies:
            self.addDependency( "a", name )

        eb = Exception()
        ec = Exception()
        ed = Exception()
        with self.unordered:
            with self.optional:
                self.getMock( "b" ).expect().andRaise( eb )
                self.getMock( "c" ).expect().andRaise( ec )
                self.getMock( "d" ).expect().andRaise( ed )

        with self.assertRaises( Action.Exception ) as cm:
            self.getAction( "a" ).execute()
        self.assertEqual( len( cm.exception.exceptions ), 1 )

class DependencyCycle( TestCase ):
    def callableFromMock( self, m ):
        return m

    def testSelfDependency( self ):
        with self.assertRaises( Exception ):
            self.addDependency( "a", "a" )

    def testShortCycle( self ):
        self.addDependency( "a", "b" )
        with self.assertRaises( Exception ):
            self.addDependency( "b", "a" )

    def testLongCycle( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "b", "c" )
        self.addDependency( "c", "d" )
        self.addDependency( "d", "e" )
        with self.assertRaises( Exception ):
            self.addDependency( "e", "a" )

class MultipleExecutions( TestCase ):
    def callableFromMock( self, m ):
        return m

    def testSimpleSuccess( self ):
        repeat = 5
        for i in range( repeat ):
            self.getMock( "a" ).expect()

        for i in range( repeat ):
            self.getAction( "a" ).execute()

    def testFailureInMiddle( self ):
        self.addDependency( "a", "b" )
        self.addDependency( "b", "c" )

        repeat = 5
        for i in range( repeat ):
            self.getMock( "c" ).expect()
            self.getMock( "b" ).expect().andRaise( Exception() )

        for i in range( repeat ):
            with self.assertRaises( Action.Exception ):
                self.getAction( "a" ).execute()

unittest.main()
