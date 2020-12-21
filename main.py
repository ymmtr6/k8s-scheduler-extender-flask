# -*- coding: utf-8 -*-
#
from flask import *
import logging
import json
import topsis

VERSION = "0.0.1"
app = Flask(__name__)

Pod_Metrics = {}
Node_Metrics = {}

with open("node_metrics.json", "r") as f:
    Node_Metrics = json.load(f)

with open("pod_metrics.json", "r") as f:
    Pod_Metrics = json.load(f)


class Node(object):

    def __init__(self, item):
        self.metadata = item.get("metadata")
        self.name = self.metadata.get("name")
        self.status = item.get("status")
        self.score = 0
        self.capacity = self.status["capacity"]
        self.allocatable = self.status["allocatable"]

    def avairable(self, use, parts="cpu"):
        allocate = int(self.allocatable.get(parts, 0))
        capacity = int(self.capacity.get(parts, 0))
        if parts == "nvidia.com/gpu":
            return allocate
        if capacity != 0:
            return (allocate - use) / capacity
        else:
            return 0.0

    def avairable_value(self, uses, parts):
        return [self.avairable(u, p) for u, p in zip(uses, parts)]


class Pod(object):

    def __init__(self, pod):
        self.name = pod.get("metadata").get("name")
        self.spec = pod.get("spec")
        self.containers = self.spec.get("containers", [])

    def use(self, parts):
        return sum([int(c.get("resources", {}).get("requests", {}).get(parts, 0)) for c in self.containers])

    def request_value(self, parts=["cpu", "ram", "nvidia.com/gpu"]):
        return [self.use(part) for part in parts]


@app.route("/")
def root():
    return "hello world"


@ app.route("/version")
def version():
    return VERSION


@ app.route("/scheduler/predicates/always_true", methods=["POST"])
def predicates():
    req = request.json
    # app.logger.debug("predicates request: " +
    #                 json.dumps(req, ensure_ascii=False))
    # Always True
    # app.logger.debug("predicates response: " + json.dumps(
    #    {"Nodes": req["Nodes"], "NodeNames": None, "FailedNodes": {}, "Error": ""}))

    # userが足りなければ，ここで切り取る
    #
    return jsonify({"Nodes": req["Nodes"], "NodeNames": None, "FailedNodes": {}, "Error": ""})


@ app.route("/scheduler/priorities/zero_score", methods=["POST"])
def priorities():
    """
    priorities
    """

    req = request.json
    pod = Pod(req["Pod"])
    nodes = [Node(n) for n in req["Nodes"]["items"]]
    #app.logger.debug("priorities request: " + json.dumps(req))
    # parts定義
    parts = ["cpu", "ram", "nvidia.com/gpu"]
    # jobのuse resource取得
    uses = pod.request_value(parts=parts)
    # Desision Matrix 生成(各nodeから作成)
    dm = [node.avairable_value(uses, parts) for node in nodes]
    app.logger.debug("decidion matrix: {}".format(dm))
    # topsisをから理想を取得
    best, worst = topsis.TOPSIS(dm).get_rank()
    # best scoreを10に
    nodes[best].score = 10

    priorities = [{"Host": n.name, "Score": n.score}
                  for n in nodes]

    app.logger.debug("priorities reseponse: " + json.dumps(priorities))
    return jsonify(priorities)


@ app.route("/preemption", methods=["POST"])
def preemption():
    return ""


@ app.route("/bind", methods=["POST"])
def bind():
    return ""


def pod_request(pod):
    cpu = 0
    gpu = 0
    ram = []
    images = []
    for container in pod["spec"]["containers"]:
        request = container.get("resources", {}).get("request", None)
        images.append(container["image"])
        if request is not None:
            cpu += float(request.get("cpu", 0))
            gpu += float(request.get("nvidia.com/gpu", 0))
            ram.append(request.get("ram", "0"))
    return cpu, gpu, ram, images


def cost(pod, node, nodeName):
    """
    "cpu_clock": 3.1,
    "cpu_core": 4,
    "ram": 16,
    "gpu": 0,
    "gpu_clock": 0,
    "gram": 0
    """
    node_score = 0
    pod_score = 0
    image = pod["metadata"]
    cpu, gpu, ram, images = pod_request(pod)
    try:
        if nodeName in Node_Metrics.keys():
            v = Node_Metrics[nodeName]
            node_score = cpu * v["cpu_clock"] + gpu * v["gpu_clock"]
        for image in images:
            if image in Pod_Metrics.keys():
                v = Pod_Metrics[image]
                pod_score = v["TIME"]
    except:
        import traceback
        traceback.print_exc()
    return {"Host": nodeName, "Score": int(node_score * pod_score)}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")
