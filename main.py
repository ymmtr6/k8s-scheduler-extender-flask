# -*- coding: utf-8 -*-
#
from flask import *
import logging
import json

VERSION = "0.0.1"
app = Flask(__name__)

Pod_Metrics = {}
Node_Metrics = {}

with open("node_metrics.json", "r") as f:
    Node_Metrics = json.load(f)

with open("pod_metrics.json", "r") as f:
    Pod_Metrics = json.load(f)


@app.route("/")
def root():
    return "hello world"


@app.route("/version")
def version():
    return VERSION


@app.route("/scheduler/predicates/always_true", methods=["POST"])
def predicates():
    req = request.json
    app.logger.debug("predicates request: " +
                     json.dumps(req, ensure_ascii=False))
    # Always True
    app.logger.debug("predicates response: " + json.dumps(
        {"Nodes": req["Nodes"], "NodeNames": None, "FailedNodes": {}, "Error": ""}))
    return jsonify({"Nodes": req["Nodes"], "NodeNames": None, "FailedNodes": {}, "Error": ""})


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


@app.route("/scheduler/priorities/zero_score", methods=["POST"])
def priorities():
    """
    priorities
    """

    req = request.json
    Pod = req["Pod"]
    Nodes = req["Nodes"]
    NodeNames = req["NodeNames"]
    node_list = [n["metadata"]["name"] for n in Nodes]

    app.logger.debug("priorities request: " + json.dumps(req))

    costs = [{"Host": n, "Score": cost(n)} for n in node_list]
    sum = sum([i["Score"] for i in costs])
    variables = 10
    priorities = [{"Host": n["Host"], "Score": (n["Score"] / sum) * variables}
                  for n in costs]

    app.logger.debug("priorities reseponse: " + json.dumps(priorities))
    return jsonify(priorities)


@app.route("/preemption", methods=["POST"])
def preemption():
    return ""


@app.route("/bind", methods=["POST"])
def bind():
    return ""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")
