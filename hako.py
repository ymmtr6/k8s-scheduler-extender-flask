# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd


c = pd.read_csv("hako2.csv", header=0)

#label = ["15_5s", "30_5s", "45_5s"]
#label = ["15_15s", "30_15s", "45_15s"]
#label = ["15_30s", "30_30s", "45_30s"]

plt.figure(figsize=(2, 4))
c.plot.box(whis="range")

plt.savefig("all4.png")
