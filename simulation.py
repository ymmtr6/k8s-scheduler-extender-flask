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
        self.p = 0

    def predicate(self, job):
        return job.ram <= self.ram and job.cpu <= self.cpu and job.gpu <= self.gpu
        # return job.cpu <= self.cpu

    def priorities(self, job):
        # return self.cpu - job.cpu
        # self.p = 4 - (self.cpu - job.cpu)
        #self.p = self.cpu - job.cpu
        self.p = self._avairable(job)
        return self.p

    def _avairable(self, job, cost=9.5):
        cost = 0
        p1 = job.ram / self.ram
        p2 = job.cpu / self.cpu
        if p1 == 1.0 or p2 == 1.0:  # Fitting
            cost += 10
        return p2 * 9.5 + p1 * 0.5

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

    def getDict(self, turn) -> dict:
        end = self.end if self.end != 0 else turn
        return {
            "name": self.name,
            "node_name": self.node_name,
            "start": self.start,
            "end": end,
        }


class Simulator(object):

    def __init__(self, nodes, jobs, turn=600):
        self.NODES = [Node(i["name"], i["ram"], i["gpu"], i["cpu"])
                      for i in nodes]
        self.JOBS = [Job(j["name"], j["ram"],  j["cpu"],
                         j["gpu"], j["time"]) for j in jobs]
        self.TURN = turn

    def run(self, verbose=False):
        # TURN = Second
        for T in range(0, self.TURN):
            # Scheduling （ランダムフェッチにするべき？）
            no_finish = [j for j in self.JOBS if not j.finish]
            # 終了処理
            if len(no_finish) == 0:
                print("FINISHED TURN: {}".format(T))
                break

            for job in no_finish:
                if job.status == "Pending":
                    # predicates
                    predicates = [n for n in self.NODES if n.predicate(job)]
                    # priorities
                    for n in predicates:
                        # prioritiesを計算
                        n.priorities(job)
                    priorities = sorted(predicates, reverse=True)
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
        #{"name": "yamato", "ram": 128, "gpu": 2, "cpu": 12}
    ]

    jobs = [
        {"name": "job1_A", "ram": 4, "gpu": 1, "cpu": 2, "time": 200},
        {"name": "job2_A", "ram": 3, "gpu": 0, "cpu": 2, "time": 100},
        {"name": "job3_B", "ram": 2, "gpu": 0, "cpu": 2, "time": 150},
        {"name": "job4_C", "ram": 5, "gpu": 0, "cpu": 2, "time": 300},
        {"name": "job5_D", "ram": 1, "gpu": 1, "cpu": 2, "time": 400},
        #{"name": "job6", "ram": 4, "gpu": 0, "cpu": 4, "time": 200},
        #{"name": "job7", "ram": 4, "gpu": 0, "cpu": 4, "time": 100},
        #{"name": "job8", "ram": 10, "gpu": 1, "cpu": 4, "time": 150},
        #{"name": "job9", "ram": 1, "gpu": 0, "cpu": 4, "time": 300}
    ]
    sim = Simulator(n, jobs, turn=600)
    sim.run(verbose=False)
    sim.plot(yticks=50, verbose=True)
