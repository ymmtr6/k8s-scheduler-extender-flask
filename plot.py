# Importing the matplotlb.pyplot
from os import times
import matplotlib.pyplot as plt
import json
import datetime
import numpy as np
import pprint
from matplotlib import colors as mcolors
from matplotlib import patches as mpatches


def plot(output="gantt1.png"):
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()
    # Setting Y-axis limits
    gnt.set_ylim(0, 50)
    # Setting X-axis limits
    gnt.set_xlim(0, 160)
    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('seconds since start')
    gnt.set_ylabel('Processor')
    # Setting ticks on y-axis
    gnt.set_yticks([15, 25, 35])
    # Labelling tickes of y-axis
    gnt.set_yticklabels(['1', '2', '3'])
    # Setting graph attribute
    gnt.grid(True)
    # Declaring a bar in schedule
    gnt.broken_barh([(40, 50)], (10, 9), facecolors=('tab:orange'))
    # Declaring multiple bars in at same level and same width
    gnt.broken_barh([(110, 10), (150, 10)], (14, 2),
                    facecolors='tab:blue')
    gnt.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
                    facecolors=('tab:red'))
    plt.savefig(output)


class God(object):

    def __init__(self, max=600, mergin=10.0):
        self.pods = {}
        self.oldest_timestamp = datetime.datetime.now()
        self.max = max
        self.mergin = mergin
        self.colors = list(mcolors.TABLEAU_COLORS.values())
        self.node_list = {}
        self.node_color = {}
        print(self.max)

    def translate_datetime(self, text):
        timestamp = datetime.datetime.fromisoformat(text.replace("Z", ""))
        return timestamp

    def load(self, json_file):
        with open(json_file) as f:
            events = json.load(f)
        items = events["items"]
        for item in items:
            reason = item.get("reason")
            if reason == "Scheduled":
                name = item.get("involvedObject").get("name").split("-")[0]
                node = item.get("message").split(" to ")[1]
                self.getPod(name)["node_name"] = node
            elif reason == "SuccessfulCreate":
                name = item.get("involvedObject").get("name")
                container_name = item.get("message").split(": ")[1]
                timestamp = item.get("firstTimestamp")
                self.getPod(name)["container_name"] = container_name
            elif reason == "Completed":
                name = item.get("involvedObject").get("name")
                timestamp = item.get("firstTimestamp")
                self.getPod(name)[
                    "end"] = self.translate_datetime(timestamp)
            elif reason == "Created":
                pass
            elif reason == "Started":
                name = item.get("involvedObject").get("name").split("-")[0]
                timestamp = item.get("firstTimestamp")
                self.getPod(name)[
                    "start"] = self.translate_datetime(timestamp)
            elif reason == "Pulling":
                pass
            elif reason == "Killing":
                pass
            elif reason == "Pulled":
                pass
            else:
                print(reason)
        for key, pod in self.pods.items():
            node_name = pod["node_name"]
            if node_name is None:
                continue
            if node_name not in self.node_list:
                self.node_list[node_name] = [pod]
            else:
                self.node_list[node_name].append(pod)

    def getPod(self, name):
        if name not in self.pods.keys():
            self.pods[name] = {
                "name": name,
                "container_name": None,
                "node_name": None,
                "start": datetime.datetime.now(),
                "end": None,
                "second": 0
            }
        return self.pods[name]

    def _second(self, date):
        if date is None:
            return self.max
        delta = date - self.oldest_timestamp
        if delta.total_seconds() < 0.0:
            return self.max
        return delta.total_seconds()

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
        self.oldest_timestamp = min([i["start"] for i in self.pods.values()])
        labels = [i for i in self.pods.keys()]
        labels.sort()

        #ticks = [i * self.mergin + self.mergin for i in range(len(labels))]
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
            s = self._second(v["start"])
            e = self._second(v["end"])
            v["second"] = e - s
            gnt.broken_barh([(s, e)], (i * self.mergin + self.mergin - 1, 2),
                            facecolors=self._color_mapping(v["node_name"]))
        plt.legend(loc="lower right", handles=self._legend())
        plt.savefig(output)

    def plot_node(self, output="gantt2"):
        fig, gnt = plt.subplots()
        self.oldest_timestamp = min([i["start"] for i in self.pods.values()])
        labels = [i for i in self.node_list.keys()]
        labels.sort()
        ticks = [i * self.mergin + self.mergin for i in range(len(labels))]
        gnt.set_ylim(0, len(labels) * self.mergin + self.mergin)
        gnt.set_xlim(0, self.max)
        gnt.set_xlabel("seconds since start")
        gnt.set_ylabel("Worker")
        gnt.set_yticks(ticks)
        gnt.set_yticklabels(labels)
        gnt.grid(True)

        for i, node_name in enumerate(labels):
            pod_list = self.node_list[node_name]
            s_e = []
            for pod in pod_list:
                s = self._second(pod["start"])
                e = self._second(pod["end"])
                s_e.append((s, e))
            gnt.broken_barh(
                s_e, (i * self.mergin + self.mergin - 1, 2), facecolors="tab:blue")
        plt.savefig(output)

    def delete_items(self, lists):
        for i in lists:
            if i in self.pods.keys():
                self.pods.pop(i)


def main(filename="event.json", output="gantt", max=600):
    obj = God(max=max)
    obj.load(filename)
    #obj.delete_items(["stress1", "stress2", "stress3"])
    obj.plot(output=output+"1.png")
    obj.plot_node(output=output+"2.png")
    pprint.pprint(obj.pods)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("output")
    parser.add_argument("-m", "--max", type=float, default=600)
    ARGS = parser.parse_args()
    print(ARGS)
    main(ARGS.file, ARGS.output, ARGS.max)
