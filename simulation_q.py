# coding: utf-8

from numpy.lib.function_base import average
from simulation_plot import God
import random
import topsis
import numpy as np


class Node(object):
    """
    node定義
    """

    def __init__(self, name, ram: int, gpu: int, cpu: int):
        self.name = name
        self.ram = ram
        self.a_ram = ram
        self.gpu = gpu
        self.a_gpu = gpu
        self.cpu = cpu
        self.a_cpu = cpu
        self.jobs = []
        self.p = 0

    def predicate(self, job):
        canAllocate = job.ram <= self.ram and job.cpu <= self.cpu and job.gpu <= self.gpu
        # wait allocate
        # if job.user == "A" and random.uniform(0, 1) < 0.8:
        #    return False
        return canAllocate

    def priorities(self, job):
        # return self.cpu - job.cpu
        # self.p = 4 - (self.cpu - job.cpu)
        # self.p = self.cpu - job.cpu
        self.p = self._avairable(job)
        return self.p

    def _avairable(self, job, cost=10):
        """
        単純にcostを実装
        """
        # avairable(利用可能を最大化) spread戦略
        cpu = (self.cpu - job.cpu) / self.a_cpu
        ram = (self.ram - job.ram) / self.a_ram
        # used最大化 binpack戦略
        # cpu = (job.cpu + (self.a_cpu - self.cpu)) / self.a_cpu
        # ram = (job.ram + (self.a_ram - self.ram)) / self.a_ram
        # gpu free
        gpu = self.gpu - job.gpu
        # print(cpu, ram, gpu)
        return cpu * ram * cost

    def cpu_avairable(self, job):
        return (self.cpu - job.cpu) / self.a_cpu

    def ram_avairable(self, job):
        return (self.ram - job.ram) / self.a_ram

    def gpu_avairable(self, job):
        return (self.gpu - job.gpu)

    def avairables(self, job):
        l = [self.cpu_avairable(job), self.ram_avairable(
            job), self.gpu_avairable(job)]
        return l

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

    def __lt__(self, other):
        return self.p < other.p


class Job(object):
    """
    Job定義
    status: Pending, Running, Completed
    """

    def __init__(self, name: str, ram: int, cpu: int, gpu: int, time: int, user="unknown"):
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
        self.user = user

    def __str__(self) -> str:
        return "{}: {}".format(self.name, self.status)

    def getDict(self, turn) -> dict:
        end = self.end if self.end != 0 else turn
        return {
            "name": self.name,
            "node_name": self.node_name,
            "start": self.start,
            "end": end,
        }


class User(object):
    """
    user定義
    """

    def __init__(self, name, count):
        self.name = name
        self.count = count


class Simulator(object):

    def __init__(self, nodes, jobs, turn=600, users=[]):
        self.NODES = [Node(i["name"], i["ram"], i["gpu"], i["cpu"])
                      for i in nodes]
        self.JOBS = [Job(j["name"], j["ram"],  j["cpu"],
                         j["gpu"], j["time"], j.get("user", "unknown")) for j in jobs]
        self.USERS = users
        self.TURN = turn

    def waiting_score(self):
        tmp = 0
        user = {}
        for u in self.USERS:
            user[u.name] = []
        for j in self.JOBS:
            user[j.user].append(j.start)
            tmp += j.start
        print("waitiong_score: ", user)
        print("waiting_score: {}, {}".format(tmp, tmp / len(self.JOBS)))
        for name, value in user.items():
            if len(value) != 0:
                print(name, sum(value) / len(value))

    def score(self):
        result = {}
        for j in self.JOBS:
            if not j.finish:
                continue
            if j["user"] not in result.keys():
                result[j.user] = 0
            else:
                result[j.user] += 0

    def priorities(self, predicates, job):
        for n in predicates:
            n.priorities(job)
        priorities = sorted(predicates, reverse=True)
        return priorities

    def topsis(self, predicates, job):
        if len(predicates) == 0:
            return predicates
        dm = [p.avairables(job) for p in predicates]
        t = topsis.TOPSIS(dm).set_isbest(np.array([True, True, False]))
        best, worst = t.get_rank()
        return [predicates[best]]

    def run(self, verbose=False):
        # TURN = Second
        for T in range(0, self.TURN):
            # Scheduling （ランダムフェッチにするべき？）
            no_finish = [j for j in self.JOBS if not j.finish]
            random.shuffle(no_finish)
            # 終了処理
            if len(no_finish) == 0:
                print("FINISHED TURN: {}".format(T))
                break

            for job in no_finish:
                if job.status == "Pending":
                    # predicates
                    predicates = [n for n in self.NODES if n.predicate(job)]
                    # priorities
                    #priorities = self.priorities(predicates, job)
                    priorities = self.topsis(predicates, job)
                    # 担当を決める(本来はスコアが同数の場合も考慮)
                    if len(priorities) != 0:
                        print(job, [(n.name, n.p)
                                    for n in priorities])
                        priorities[0].add(T, job)
                        job.status = "Running"

            # Process
            for node in self.NODES:
                node.clock(T)

            # Verbose
            if verbose:
                print("TURN:{}, ".format(T), end="")
                for node in self.NODES:
                    print("{}, ".format(node), end="")
                for job in self.JOBS:
                    print("{}: {}, ".format(job.name, job.status), end="")
                print("")

        for job in self.JOBS:
            print("{}: {}, ".format(job.name, job.status), end="")

    def plot(self, output="sample.png", yticks=60.0, mergin=10.0, verbose=False):
        pods = {}
        for job in self.JOBS:
            pods[job.name] = job.getDict(turn=self.TURN)
        print(pods)
        god = God(pods=pods, max=self.TURN, mergin=mergin)
        god.plot(output=output, verbose=verbose, yticks=yticks)


if __name__ == "__main__":
    n = [
        {"name": "node2", "ram": 16, "gpu": 0, "cpu": 4},
        {"name": "node3", "ram": 6, "gpu": 1, "cpu": 4},
        {"name": "node4", "ram": 10, "gpu": 1, "cpu": 4},
        # {"name": "yamato", "ram": 128, "gpu": 2, "cpu": 12}
    ]

    u = [
        {"name": "A", "count": 1},
        {"name": "B", "count": 2},
        {"name": "C", "count": 3},
        {"name": "D", "count": 5}
    ]

    jobs = [
        {"name": "job01_A", "ram": 4, "gpu": 1,
            "cpu": 4, "time": 200, "user": "A"},
        {"name": "job02_A", "ram": 3, "gpu": 0,
            "cpu": 4, "time": 100, "user": "A"},
        {"name": "job03_B", "ram": 2, "gpu": 0,
            "cpu": 4, "time": 150, "user": "B"},
        {"name": "job04_C", "ram": 5, "gpu": 0,
            "cpu": 4, "time": 300, "user": "B"},
        {"name": "job05_D", "ram": 1, "gpu": 1,
            "cpu": 4, "time": 400, "user": "C"},
        {"name": "job06_A", "ram": 4, "gpu": 0,
            "cpu": 4, "time": 200, "user": "A"},
        {"name": "job07_A", "ram": 4, "gpu": 0, "cpu": 4, "time": 100,
         "user": "A"},
        {"name": "job08_A", "ram": 10, "gpu": 1, "cpu": 4, "time": 150,
         "user": "A"},
        {"name": "job09_C", "ram": 1, "gpu": 0, "cpu": 4, "time": 300,
         "user": "C"},
        {"name": "job10_D", "ram": 1, "gpu": 0, "cpu": 4, "time": 300,
         "user": "D"}
    ]

    sim = Simulator(n, jobs, turn=900, users=[
                    User(i["name"], i["count"])for i in u])
    sim.run(verbose=False)
    sim.plot(yticks=50, verbose=True)
    sim.waiting_score()
