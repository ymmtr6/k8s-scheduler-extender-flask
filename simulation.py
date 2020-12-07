# coding: utf-8

from simulation_plot import God


class Node(object):
    """
    node定義
    """

    def __init__(self, name, ram: int, gpu: int, cpu: int):
        self.name = name
        self.ram = ram
        self.gpu = gpu
        self.cpu = cpu
        self.jobs = []

    def predicate(self, job):
        return job.ram <= self.ram and job.cpu <= self.cpu and job.gpu <= self.gpu
        # return job.cpu <= self.cpu

    def priorities(self, job):
        # return self.cpu - job.cpu
        return 4 - (self.cpu - job.cpu)

    def add(self, T, job):
        self.jobs.append(job)
        job.start = T
        job.node_name = self.name
        self.ram -= job.ram
        self.gpu -= job.gpu
        self.cpu -= job.cpu

    def remove(self, T, job):
        # print("REMOVE JOB: {}".format(job.name))
        job.finish = True
        job.status = "Completed"
        job.end = T
        self.ram += job.ram
        self.gpu += job.gpu
        self.cpu += job.cpu

    def clock(self, T):
        for j in self.jobs:
            if T - j.start >= j.time:
                self.remove(T, j)
        # 更新
        self.jobs = [j for j in self.jobs if not j.finish]

    def __str__(self):
        return "{}: {}({})".format(self.name, self.cpu, [j.name for j in self.jobs])


class Job(object):
    """
    Job定義
    status: Pending, Running, Completed
    """

    def __init__(self, name, ram: int, cpu: int, gpu: int, time: int):
        self.status = "Pending"
        self.name = name
        self.ram = ram
        self.gpu = gpu
        self.cpu = cpu
        self.time = time
        self.start = 0
        self.end = 0
        self.finish = False
        self.node_name = "Pending"

    def __str__(self) -> str:
        return "{}: {}".format(self.name, self.status)

    def getDict(self) -> dict:
        end = self.end if self.end != 0 else TURN
        return {
            "name": self.name,
            "node_name": self.node_name,
            "start": self.start,
            "end": end,
        }


n = [
    {"name": "node2", "ram": 16, "gpu": 0, "cpu": 4},
    {"name": "node3", "ram": 6, "gpu": 1, "cpu": 4},
    {"name": "node4", "ram": 10, "gpu": 1, "cpu": 4}
]

jobs = [
    {"name": "job1", "ram": 2, "gpu": 0, "cpu": 2, "time": 200},
    {"name": "job2", "ram": 1, "gpu": 0, "cpu": 4, "time": 100},
    {"name": "job3", "ram": 2, "gpu": 0, "cpu": 2, "time": 150},
    {"name": "job4", "ram": 2, "gpu": 0, "cpu": 4, "time": 300},
    #    {"name": "job5", "ram": 1, "gpu": 0, "cpu": 3, "time": 500}
]

Nodes = [Node(i["name"], i["ram"], i["gpu"], i["cpu"]) for i in n]
Jobs = [Job(j["name"], j["ram"],  j["cpu"], j["gpu"], j["time"]) for j in jobs]
TURN = 600

Scheduler = [[0 for i in range(TURN)] for i in Nodes]

print("INIT, ", end="")
for node in Nodes:
    print("{},".format(node), end="")
print()

for T in range(0, TURN):
    # check job
    print("TURN:{}, ".format(T), end="")

    for job in Jobs:  # 　本来Jobはランダムフェッチ
        if job.status == "Pending":
            predicates = [n.predicate(job) for n in Nodes]
            #print([n for n in Nodes if n.predicate(job)])
            priorities = [n.priorities(job) for n in Nodes]
            for i, p in enumerate(predicates):
                if not p:
                    priorities[i] = -1
            # 本来はスコアが同数の場合も考慮する
            target = priorities.index(max(priorities))
            # print(target)
            if predicates[target]:
                Nodes[target].add(T, job)
                job.status = "Running"

    for node in Nodes:
        node.clock(T)
        print("{}, ".format(node), end="")

    for job in Jobs:
        print("{}: {}, ".format(job.name, job.status), end="")
    print()

pods = {}
for job in Jobs:
    pods[job.name] = job.getDict()
print([i for i in pods.keys()])
obj = God(pods=pods, max=TURN)

obj.plot(output="sample2.png")
