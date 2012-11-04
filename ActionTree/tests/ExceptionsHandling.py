# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import Framework

from ActionTree.Action import Action


class ExceptionsHandling( Framework.TestCase ):
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
        self.assertTrue( eb in cm.exception.exceptions )
        self.assertTrue( ec in cm.exception.exceptions )

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
            with self.optional:
                self.getMock( "c" ).expect().andRaise( ec )
            with self.optional:
                self.getMock( "d" ).expect().andRaise( ed )

        with self.assertRaises( Action.Exception ) as cm:
            self.getAction( "a" ).execute()
        self.assertEqual( len( cm.exception.exceptions ), 1 )
        self.assertTrue( cm.exception.exceptions[ 0 ] in [ eb, ec, ed ] )
