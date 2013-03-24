# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import math


class ExecutionReport:
    def __init__(self, action):
        self.__actions = []
        self.__gatherInformation(action)
        self.__consolidate()

    def __gatherInformation(self, action, seenActions=list()):
            action.getDependencies()
        # if action not in seenActions:
            # seenActions.append(action)
            # for dependency in action.getDependencies():
                # dependency.__gatherInformation(seenActions)
            self.__actions.append((action.beginTime, action.endTime, action.status))

    def __consolidate(self):
        self.__beginTime = math.floor(min(a[0] for a in self.__actions))
        self.__endTime = math.ceil(max(a[1] for a in self.__actions))
        self.__duration = self.__endTime - self.__beginTime

    def getHeight(self, ctx):
        return 10 + len(self.__actions) * 20

    def draw(self, ctx, width):
        ctx.translate(10, 0)
        ctx.scale((width - 20) / self.__duration, 1)
        ctx.translate(-self.__beginTime, 0)

        self.__drawTimeLine(ctx)
        ctx.translate(0, 10)

        for action in self.__actions:
            self.__drawAction(action, ctx, width)
            ctx.translate(0, 20)

    def __drawTimeLine(self, ctx):
        ctx.move_to(self.__beginTime, 5)
        ctx.line_to(self.__endTime, 5)
        ctx.stroke()

    def __drawAction(self, action, ctx, width):
        ctx.move_to(action[0], 10)
        ctx.line_to(action[1], 10)
        ctx.stroke()
