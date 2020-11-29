# -*- coding: utf-8 -*-
#
from flask import *
import logging
import json

VERSION = "0.0.1"
app = Flask(__name__)


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


def cost(node, nodeName):
    """
    ここにロジックをかく．
    """
    score = 0
    return {"Host": nodeName, "Score": score}


@app.route("/scheduler/priorities/zero_score", methods=["POST"])
def priorities():
    """
    priorities
    """
    priorities = []

    req = request.json
    Pod = req["Pod"]
    Nodes = req["Nodes"]
    NodeNames = req["NodeNames"]

    app.logger.debug("priorities request: " + json.dumps(req))

    # parse nodes
    for item in Nodes["items"]:
        name = item["metadata"]["name"]
        priorities.append(cost(item, name))

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
