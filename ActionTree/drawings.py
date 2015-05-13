# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import math

import cairo
import graphviz

from . import Action


class ExecutionReport:
    """
    Draw a report of the execution of the action, showing successes and failures as well as timing information.

    :param Action action: the subject of the report.
    """
    class Action:
        def __init__(self, label, begin_time, end_time, status):
            self.label = label
            self.begin_time = begin_time
            self.end_time = end_time
            self.status = status
            self.dependencies = []
            self.ordinate = 0

    def __init__(self, action):
        self.__actions = []
        self.__root = None
        self.__gather_information(action)
        self.__consolidate()

    def __gather_information(self, root):
        seen_actions = {}

        def create(action):
            action_id = id(action)
            if action_id not in seen_actions:
                a = ExecutionReport.Action(str(action.label), action.begin_time, action.end_time, action.status)
                seen_actions[action_id] = a
                for dependency in action.get_dependencies():
                    a.dependencies.append(create(dependency))
            return seen_actions[action_id]

        self.__root = create(root)
        self.__actions = list(seen_actions.values())

    def __consolidate(self):
        self.__begin_time = math.floor(min(a.begin_time for a in self.__actions))
        self.__end_time = math.ceil(max(a.end_time for a in self.__actions))
        self.__duration = self.__end_time - self.__begin_time
        self.__compute_ordinates()

    def __compute_ordinates(self):
        def compute(action, from_ordinate):
            action.ordinate = from_ordinate
            dependencies = sorted(action.dependencies, key=lambda d: d.end_time)
            for i, d in enumerate(dependencies):
                compute(d, from_ordinate - (i + 1) * 20)
        compute(self.__root, 20 * (len(self.__actions) - 1))

    def write_to_png(self, fobj, width=800):
        """
        Write the report as a PNG image.

        :param fobj: a file name or an open file, passed to :meth:`cairo.Surface.write_to_png`.
        :param int width: the width in pixel of the image to produce. (Its height will be computed internaly.)
        """
        height = self.get_height(cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)))
        image = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(image)
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0)
        self.draw(ctx, width)
        image.write_to_png(fobj)

    def draw(self, ctx, width=800):
        """
        Draw the report to a :class:`cairo.Context`.
        You'll probably want to use :meth:`get_height` to know what will be inked.

        :param cairo.Context ctx:
        :param int width: the width in logical units of the image to produce.
        """
        ctx.save()

        ctx.translate(10, 0)
        ctx.scale((width - 20) / self.__duration, 1)
        ctx.translate(-self.__begin_time, 0)

        self.__draw_time_line(ctx)
        ctx.translate(0, 10)

        for action in self.__actions:
            self.__draw_action(action, ctx, width)

        ctx.restore()

    def get_height(self, ctx):
        """
        Return the height that would be occupied by the report if drawn on ``ctx``.

        Typical usage::

            width = 800
            height = report.get_height(cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)))
            image = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
            ctx = cairo.Context(image)
            report.draw(ctx, width)

        (But :meth:`write_to_png` does that for you, so this method is useful to draw on an arbitrary :class:`cairo.Context`.)

        :param cairo.Context ctx:
        """
        return 10 + len(self.__actions) * 20

    def __draw_time_line(self, ctx):
        ctx.move_to(self.__begin_time, 5)
        ctx.line_to(self.__end_time, 5)
        ctx.stroke()

    def __draw_action(self, action, ctx, width):
        ctx.save()
        ctx.translate(0, action.ordinate)

        ctx.save()
        ctx.set_line_width(4)
        ctx.move_to(action.begin_time, 18)
        ctx.line_to(action.end_time, 18)
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
            ctx.move_to(action.begin_time, 18)
            ctx.line_to(d.end_time, d.ordinate - action.ordinate + 18)
        ctx.set_line_width(1)
        ctx.identity_matrix()
        ctx.set_source_rgb(0.7, 0.7, 0.7)
        ctx.stroke()
        ctx.restore()

        ctx.move_to(action.begin_time, 15)
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


# @todo Should there be a class Graph with a method get_graphviz_graph?
# This would allow implementing graphs in other libraries without creating more free functions.
# Same for execution reports.


def make_graph(action, format="png"):
    """
    Build a :class:`graphviz.Digraph` representing the action and its dependencies.
    """
    g = GraphBuilder(action).graph
    g.format = format
    return g
