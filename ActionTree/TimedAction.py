# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import time

import Action


class TimedAction( Action.Action ):
    time = time.time  # Allow static dependency injection

    def __init__( self, execute, label ):
        self.__execute = execute
        Action.Action.__init__( self, self.__timedExecute, label )

    def __timedExecute( self ):
        self.beginTime = self.time()
        try:
            self.__execute()
        finally:
            self.endTime = self.time()
