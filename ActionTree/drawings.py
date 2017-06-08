# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

# from __future__ import division, absolute_import, print_function

# import collections
# import datetime
# import os.path

# import graphviz
# import matplotlib.backends.backend_agg
# import matplotlib.dates
# import matplotlib.figure as mpl

# from . import Action


def nearest(v, values):
    for i, value in enumerate(values):
        if v < value:
            break
    if i == 0:
        return values[0]
    else:
        if v - values[i - 1] <= values[i] - v:
            return values[i - 1]
        else:
            return values[i]

# intervals = [
#     1, 2, 5, 10, 15, 30, 60,
#     2 * 60, 10 * 60, 30 * 60, 3600,
#     2 * 3600, 3 * 3600, 6 * 3600, 12 * 3600, 24 * 3600,
# ]


# _FrozenAction = collections.namedtuple(
#     "_FrozenAction",
#     # "label, dependencies, dependents, begin_time, end_time, status, notes"
#     "label, dependencies, dependents, notes"
# )


# def freeze(action, notes_factory, seen=None):
#     if seen is None:
#         seen = {}
#     if id(action) not in seen:
#         dependencies = [freeze(d, notes_factory, seen)[id(d)] for d in action.dependencies]
#         a = _FrozenAction(
#             str(action.label),
#             dependencies,
#             [],
#             # action.begin_time,
#             # action.end_time,
#             # action.status,
#             notes_factory()
#         )
#         for d in dependencies:
#             d.dependents.append(a)
#         seen[id(action)] = a
#     return seen


# @todo Restore

# class ExecutionReport(object):
#     """
#     Report about the execution of the action, containing successes and failures as well as timing information.
#     """

#     class Annotations(object):
#         def __init__(self):
#             self.dependents = set()
#             self.ordinate = None

#     def __init__(self, action):
#         actions = freeze(action, self.Annotations)
#         self.root_action = actions[id(action)]
#         self.actions = self.__sort_actions(actions.values())
#         self.begin_time = min(a.begin_time for a in self.actions)
#         self.end_time = max(a.end_time for a in self.actions)
#         self.duration = self.end_time - self.begin_time

#     def __sort_actions(self, actions):
#         for action in actions:
#             action.notes.dependents = set(id(d) for d in action.dependents)

#         def compute(action, ordinate):
#             action.notes.ordinate = ordinate
#             for d in sorted(action.dependencies, key=lambda d: d.end_time):
#                 if len(d.notes.dependents) == 1:
#                     ordinate = compute(d, ordinate - 1)
#                 else:
#                     d.notes.dependents.remove(id(action))
#             return ordinate
#         last_ordinate = compute(self.root_action, len(actions) - 1)

#         assert last_ordinate == 0, last_ordinate

#         return sorted(actions, key=lambda a: a.notes.ordinate)
#         # @todo Maybe count intersections and do a local search (two-three steps) to see if we can remove some of them

#     def write_to_png(self, filename):  # pragma no cover (Untestable? But small.)
#         """
#         Write the report as a PNG image to the specified file.

#         See also :meth:`get_mpl_figure` and :meth:`plot_on_mpl_axes` if you want to draw the report somewhere else.
#         """
#         figure = self.get_mpl_figure()
#         canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(figure)
#         canvas.print_figure(filename)

#     def get_mpl_figure(self):  # pragma no cover (Untestable? But small.)
#         """
#         Return a :class:`matplotlib.figure.Figure` of this report.

#         See also :meth:`plot_on_mpl_axes` if you want to draw the report on your own matplotlib figure.

#         See also :meth:`write_to_png` for the simplest use-case.
#         """
#         fig = mpl.Figure()
#         ax = fig.add_subplot(1, 1, 1)

#         self.plot_on_mpl_axes(ax)

#         return fig

#     def plot_on_mpl_axes(self, ax):
#         """
#         Plot this report on the provided :class:`matplotlib.axes.Axes`.

#         See also :meth:`write_to_png` and :meth:`get_mpl_figure` for the simpler use-cases.
#         """
#         ordinates = {id(a): len(self.actions) - i for i, a in enumerate(self.actions)}

#         for a in self.actions:
#             if a.status == Action.Successful:
#                 color = "blue"
#             elif a.status == Action.Failed:
#                 color = "red"
#             else:  # Canceled
#                 color = "gray"
#             ax.plot([a.begin_time, a.end_time], [ordinates[id(a)], ordinates[id(a)]], color=color, lw=4)
#             ax.annotate(a.label, xy=(a.begin_time, ordinates[id(a)]), xytext=(0, 3), textcoords="offset points")
#             for d in a.dependencies:
#                 ax.plot([d.end_time, a.begin_time], [ordinates[id(d)], ordinates[id(a)]], "k:", lw=1)

#         ax.get_yaxis().set_ticklabels([])
#         ax.set_ylim(0.5, len(self.actions) + 1)

#         min_time = self.begin_time.replace(microsecond=0)
#         max_time = self.end_time.replace(microsecond=0) + datetime.timedelta(seconds=1)
#         duration = int((max_time - min_time).total_seconds())

#         ax.set_xlabel("Local time")
#         ax.set_xlim(min_time, max_time)
#         ax.xaxis_date()
#         ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
#         ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(maxticks=4, minticks=5))

#         ax2 = ax.twiny()
#         ax2.set_xlabel("Relative time")
#         ax2.set_xlim(min_time, max_time)
#         ticks = range(0, duration, nearest(duration // 5, intervals))
#         ax2.xaxis.set_ticks([self.begin_time + datetime.timedelta(seconds=s) for s in ticks])
#         ax2.xaxis.set_ticklabels(ticks)
