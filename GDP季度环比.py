import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import akshare as ak
import gp


df = gp.get_gdp()
df = df[df["quarter"] > "2010"]  # 2000 年后
df = df.sort_values(by="quarter", ascending=True).reset_index(drop=True)  # 排序


gdp增长 = []
前三月gdp = 0
for i in range(len(df["gdp"])):
    本月gdp = df["gdp"][i]
    if i == 0:
        本月gdp = df["gdp"][i]
        前三月gdp = 本月gdp
    elif "Q1" in df["quarter"][i]:
        本月gdp = df["gdp"][i]  # - (df["gdp"][i - 1] - df["gdp"][i - 2])
    else:
        本月gdp = df["gdp"][i] - df["gdp"][i - 1]

    gdp增长.append(本月gdp - 前三月gdp)
    # print(f"{本月gdp} - {前三月gdp}")

    前三月gdp = 本月gdp
# df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)  # 季度转日期
plt.plot(df["quarter"], gdp增长)
plt.grid(True)
plt.show()
