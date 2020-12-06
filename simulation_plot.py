# Importing the matplotlb.pyplot
from os import times
import matplotlib.pyplot as plt
import json
import datetime
import numpy as np
import pprint
from matplotlib import colors as mcolors
from matplotlib import patches as mpatches


class God(object):

    def __init__(self, pods={}, max=600, mergin=10.0):
        self.pods = pods
        self.max = max
        self.mergin = mergin
        self.colors = list(mcolors.TABLEAU_COLORS.values())
        self.node_list = {}
        self.node_color = {}
        self.labels = [i for i in self.pods.keys()]

    def _color_mapping(self, node):
        if node not in self.node_color.keys():
            self.node_color[node] = self.colors[len(self.node_color)]
        return self.node_color[node]

    def _legend(self):
        node_name = [i for i in self.node_color.keys()]
        node_name.sort()
        return [mpatches.Patch(color=self._color_mapping(i), label=i) for i in node_name]

    def plot(self, output="gantt1.png"):
        fig, gnt = plt.subplots()
        print(self)
        labels = self.labels
        labels.sort()
        # ticks = [i * self.mergin + self.mergin for i in range(len(labels))]
        gnt.set_ylim(0, len(labels) * self.mergin + self.mergin)
        gnt.set_xlim(0, self.max)
        gnt.set_xlabel("seconds since start")
        gnt.set_ylabel("Job")
        gnt.set_yticks(np.arange(self.mergin, len(labels) *
                                 self.mergin + self.mergin, self.mergin))
        gnt.set_xticks(np.arange(0.0, self.max + 1.0, 60.0))
        gnt.set_yticklabels(labels)
        gnt.grid(True)

        for i, label in enumerate(labels):
            v = self.pods[label]
            print(v)
            s = v["start"]
            e = v["end"]
            gnt.broken_barh([(s, e)], (i * self.mergin + self.mergin - 1, 2),
                            facecolors=self._color_mapping(v["node_name"]))
        plt.legend(loc="lower right", handles=self._legend())
        plt.savefig(output)