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
        self.node_color = {
            # "node2": self.colors[0],
            # "node3": self.colors[1],
            # "node4": self.colors[2],
            # "nagato": self.colors[3],
            # "node1": self.colors[3]
            "node2": "0.2",
            "node3": "0.4",
            "node4": "0.6",
            "nagato": "0.8",
            "node1": "0.8"
        }
        self.hatches = {
            "node2": "xxx",
            "node3": "||",
            "node4": "--",
            "nagato": "..",
            "node1": ".."
        }
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
                pass
                # print(reason)
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
        # return [mpatches.Patch(color=self._color_mapping(i), label=i, hatch=self.hatches[i]) for i in node_name]
        # eturn [mpatches.Patch(facecolor=self._color_mapping(i), label=i, hatch=self.hatches[i]) for i in node_name]
        return [mpatches.Patch(facecolor=self._color_mapping(i), edgecolor="0.0", label=i, hatch=self.hatches[i]) for i in node_name if i != "nagato"]

    def plot(self, output="gantt1.png", x_mergin=60, job_num=15, subplot=1, fig=plt.figure()):
        gnt = fig.add_subplot(2, 1, subplot)
        self.oldest_timestamp = min([i["start"] for i in self.pods.values()])
        labels = [i for i in self.pods.keys()]
        labels.sort()

        #ticks = [i * self.mergin + self.mergin for i in range(len(labels))]
        gnt.set_ylim(0, len(labels) * self.mergin + self.mergin)
        gnt.set_xlim(0, self.max)
        gnt.set_xticks(np.arange(0.0, self.max + 1.0, x_mergin))
        if subplot == 2:
            gnt.set_xlabel("seconds since start")
            gnt.set_title("our method")
        else:
            gnt.set_title("default")
            gnt.set_xticklabels([])

        gnt.set_ylabel("Job ID")
        gnt.set_yticks(np.arange(self.mergin, len(labels) *
                                 self.mergin + self.mergin, self.mergin))
        gnt.set_yticklabels([l.replace("job", "") for l in labels])
        gnt.set_axisbelow(True)
        gnt.grid(True)

        for i, label in enumerate(labels):
            v = self.pods[label]
            s = self._second(v["start"])
            e = self._second(v["end"])
            print("{},{},{}".format(label, s, e))
            v["second"] = e - s
            width = 8
            # gnt.broken_barh([(s, v["second"])], (i * self.mergin + self.mergin - (width // 2), width),
            #                 facecolors=self._color_mapping(v["node_name"]))
            bottom = i * self.mergin + self.mergin
            gnt.barh(
                bottom,
                v["second"],
                height=width,
                left=s,
                color=self._color_mapping(v["node_name"]),
                # color="1.0",
                edgecolor="0.0",
                hatch=self.hatches[v["node_name"]]
            )
        # plt.legend(loc="lower right",
        #           handles=self._legend(), fontsize=14)
        # plt.show()
        # plt.savefig(output)

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


def main(filename="event.json", output="gantt", max=600, mergin=60):
    obj = God(max=max)
    obj.load(filename)
    obj2 = God(max=max)
    obj2.load("default_p.json")

    fig = plt.figure()
    #obj.delete_items(["stress1", "stress2", "stress3"])
    obj2.plot(output="none.jpng", x_mergin=mergin, subplot=1, fig=fig)
    obj.plot(output=output+"1.png", x_mergin=mergin, fig=fig, subplot=2)

    plt.legend(loc="lower right",
                   handles=obj._legend(), fontsize=12)
    plt.show()
    # plt.savefig(output)
    # obj.plot_node(output=output+"2.png")
    # pprint.pprint(obj.pods)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("output")
    parser.add_argument("-m", "--max", type=float, default=600)
    parser.add_argument("--mergin", type=float, default=60)
    ARGS = parser.parse_args()
    print(ARGS)
    main(ARGS.file, ARGS.output, ARGS.max, ARGS.mergin)
