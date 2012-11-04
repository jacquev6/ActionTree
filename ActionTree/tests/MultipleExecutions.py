# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import Framework

from ActionTree.Action import Action


class MultipleExecutions( Framework.TestCase ):
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
