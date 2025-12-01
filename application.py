from flask import Flask, request, Response
import os
import json

from kubernetes import client, config
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNTER = Counter(
    "greetings_requests_total",
    "Total number of requests received by the greetings application endpoints",
    ["endpoint"],
)


@app.route("/")
def hello():
    REQUEST_COUNTER.labels(endpoint="root").inc()
    return "Hello World!"


@app.route("/greetings")
def greetings():
    REQUEST_COUNTER.labels(endpoint="greetings").inc()
    greeting = os.getenv("GREETING")
    return greeting


@app.route("/listcontents")
def listcontents():
    REQUEST_COUNTER.labels(endpoint="listcontents").inc()
    contents = os.listdir("/hostfolder")
    fp = open("/hostfolder/filenames.txt","r")
    lines = fp.readlines()
    return lines


@app.route("/getk8sobjects")
def get_cluster_details():
    REQUEST_COUNTER.labels(endpoint="getk8sobjects").inc()
    config.load_incluster_config()

    namespace = "default"
    
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)

    output = {}

    pod_names = []
    for pod in pods.items:
        pod_names.append(pod.metadata.name)
    output["pods"] = pod_names

    cfg_map_names = []
    configmaps = v1.list_namespaced_config_map(namespace)
    for configmap in configmaps.items:
        cfg_map_names.append(configmap.metadata.name)
    output["configmaps"] = cfg_map_names

    sa_names = []
    serviceaccounts = v1.list_namespaced_service_account(namespace)
    for serviceaccount in serviceaccounts.items:
        sa_names.append(serviceaccount.metadata.name)
    output["serviceaccounts"] = sa_names

    obj_to_return = json.dumps(output)
    return obj_to_return


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
