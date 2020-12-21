# coding: utf-8

import datetime
import csv
import subprocess

CMD = "kubectl top node"
date = datetime.datetime.now()
input = [i.split() for i in subprocess.Popen(CMD, stdout=subprocess.PIPE,
                                             shell=True).stdout.read().decode("utf-8").split("\n")[1:]]

for i in input:
    with open("{}.csv".format(i[0]), "a") as f:
        writer = csv.writer(f)
        writer.writerow([date] + i[1:])
