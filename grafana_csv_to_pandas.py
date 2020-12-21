# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


CSV_FILE_NAME = "11-30_12-06_container.csv"

df = pd.read_csv(CSV_FILE_NAME, header=None, sep=";")
SKIP = 128

all_containers = df[0].unique()

NAMES = {}
for i in all_containers:
    d = eval(i.replace('hostname', '"hostname"').replace(
        ',name', ',"name"').replace("=", ":"))
    if d["name"] not in NAMES.keys():
        NAMES[d["name"]] = [i]
    else:
        NAMES[d["name"]].append(i)

for key, values in NAMES.items():
    # Containerそれぞれに分解し，数値に対して名前を設定する．
    result = pd.concat([df[df[0] == name].loc[:, [1, 2]].rename(
        columns={1: "TIMESTUMP", 2: name}) for name in values], ignore_index=True)
    # datetimeを変更
    result.index = pd.to_datetime(result["TIMESTUMP"])
    result = result.drop("TIMESTUMP", axis=1)
    # 欠損値を0補完
    result = result.fillna(0)

    fig, ax = plt.subplots(figsize=(20, 10))
    # for label, items in result.iteritems():
    #    print(label)
    #    ax.plot(result.index, items, label=label, alpha=0.8)
    ax = result.plot(alpha=0.5, rot=90, grid=True, figsize=(20, 10))
    # ax.grid()
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    # ax.legend()
    #plt.setp(ax.get_xticklabels(), rotation=90)
    # ax.set_xticks(result.index[::SKIP])
    #ax.set_xticklabels([t.time() for t in result.index[::SKIP]])
    # plt.show()
    plt.savefig("images/{}.png".format(key))
    plt.close("all")
