# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import patches as mpatches


#files = ["15s_o (2).csv"]
files = ["fix.csv"]
colors = ["blue", "black", "red", "green"]
users = ["m", "y", "i", "k"]
secret = ["A", "B", "C", "D"]
fig, axes = plt.subplots(1, 1, figsize=(5, 5))

for f, ax in zip(files, [axes]):
    data = pd.read_csv("集計 - " + f)
    # for user, color, s in zip(users, colors, secret):
    #     # data[data["user"] == user].plot.scatter(
    #     #    x="our method", y="ds", ax=ax, color=color, label=s, grid=True)
    #     data[data["user"] == user].plot.hist()
    #     break
    #print(data[data["user"] == "k"])
    #data[data["user"] == "k"].plot.hist(ax=ax, bins=25, alpha=0.5)
    data[data["user"] == "y"].plot.hist(
        ax=ax, bins=25, alpha=0.5)
    ax.set_ylim(0, 36)
plt.show()
