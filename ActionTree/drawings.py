# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import math
import graphviz

from . import Action


class ExecutionReport:
    class Action:
        def __init__(self, label, beginTime, endTime, status):
            self.label = label
            self.beginTime = beginTime
            self.endTime = endTime
            self.status = status
            self.dependencies = []
            self.ordinate = 0

    def __init__(self, action):
        self.__actions = []
        self.__root = None
        self.__gatherInformation(action)
        self.__consolidate()

    def __gatherInformation(self, root):
        seenActions = {}

        def create(action):
            actionId = id(action)
            if actionId not in seenActions:
                a = ExecutionReport.Action(str(action.label), action.beginTime, action.endTime, action.status)
                seenActions[actionId] = a
                for dependency in action.getDependencies():
                    a.dependencies.append(create(dependency))
            return seenActions[actionId]

        self.__root = create(root)
        self.__actions = list(seenActions.values())

    def __consolidate(self):
        self.__beginTime = math.floor(min(a.beginTime for a in self.__actions))
        self.__endTime = math.ceil(max(a.endTime for a in self.__actions))
        self.__duration = self.__endTime - self.__beginTime
        self.__computeOrdinates()

    def __computeOrdinates(self):
        def compute(action, fromOrdinate):
            action.ordinate = fromOrdinate
            dependencies = sorted(action.dependencies, key=lambda d: d.endTime)
            for i, d in enumerate(dependencies):
                compute(d, fromOrdinate - (i + 1) * 20)
        compute(self.__root, 20 * (len(self.__actions) - 1))

    def getHeight(self, ctx):
        return 10 + len(self.__actions) * 20

    def draw(self, ctx, width):
        ctx.save()

        ctx.translate(10, 0)
        ctx.scale((width - 20) / self.__duration, 1)
        ctx.translate(-self.__beginTime, 0)

        self.__drawTimeLine(ctx)
        ctx.translate(0, 10)

        for action in self.__actions:
            self.__drawAction(action, ctx, width)

        ctx.restore()

    def __drawTimeLine(self, ctx):
        ctx.move_to(self.__beginTime, 5)
        ctx.line_to(self.__endTime, 5)
        ctx.stroke()

    def __drawAction(self, action, ctx, width):
        ctx.save()
        ctx.translate(0, action.ordinate)

        ctx.save()
        ctx.set_line_width(4)
        ctx.move_to(action.beginTime, 18)
        ctx.line_to(action.endTime, 18)
        if action.status == Action.Successful:
            ctx.set_source_rgb(0, 0, 0)
        elif action.status == Action.Canceled:
            ctx.set_source_rgb(.4, .4, .4)
        else:
            ctx.set_source_rgb(1, 0, 0)
        ctx.stroke()
        ctx.restore()

        ctx.save()
        for d in action.dependencies:
            ctx.move_to(action.beginTime, 18)
            ctx.line_to(d.endTime, d.ordinate - action.ordinate + 18)
        ctx.set_line_width(1)
        ctx.identity_matrix()
        ctx.set_source_rgb(0.7, 0.7, 0.7)
        ctx.stroke()
        ctx.restore()

        ctx.move_to(action.beginTime, 15)
        ctx.save()
        ctx.identity_matrix()
        ctx.set_font_size(15)
        ctx.set_source_rgb(0, 0, 0)
        ctx.show_text(action.label)
        ctx.restore()

        ctx.restore()


class GraphBuilder(object):
    def __init__(self, action):
        self.__nodes = dict()
        self.__next_node = 0
        self.graph = graphviz.Digraph("action", node_attr={"shape": "box"})
        self.__create_node(action)

    def __create_node(self, a):
        if id(a) not in self.__nodes:
            node = str(self.__next_node)
            label = str(a.label)
            self.graph.node(node, label)
            self.__next_node += 1
            for d in a.dependencies:
                self.graph.edge(node, self.__create_node(d))
            self.__nodes[id(a)] = node
        return self.__nodes[id(a)]


def make_graph(action, format="png"):
    """
    Build a :class:`graphviz.Digraph` representing the action and its dependencies.
    """
    g = GraphBuilder(action).graph
    g.format = format
    return g
