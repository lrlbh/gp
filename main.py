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
        本月gdp = df["gdp"][i] #- (df["gdp"][i - 1] - df["gdp"][i - 2])
    else:
        本月gdp = df["gdp"][i] - df["gdp"][i - 1]

    # print(f"本月GDP{本月gdp}")

    gdp增长.append(本月gdp - 前三月gdp)
    # gdp增长.append(本月gdp)
    print(f"{本月gdp} - {前三月gdp}")

    前三月gdp = 本月gdp
df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)  # 季度转日
plt.plot(df["quarter"], gdp增长)
plt.grid(True)
plt.show()

# print(df)

# df = gp.get_m2()
# df = df.iloc[::-1].reset_index(drop=True)
# m2x = []
# m2 = []
# for row in df.itertuples():
#     if row.month > 2000:
#         m2x.append(int(row.month))
#         m2.append(row.m2)


# def normalize(series):
#     return (series - series.min()) / (series.max() - series.min())


# # 大家都变成了 0~1 的相对高度，完美自适应
# plt.plot(df["month"], normalize(df["m2"]), label="M2 (Normalized)", color="blue")
# plt.plot(df["month"], normalize(df["m1"]), label="M1 (Normalized)", color="orange")
# plt.plot(df["month"], normalize(df["m0"]), label="M0 (Normalized)", color="green")
# plt.grid(True)
# plt.show()

# 1/0

# gp.更新()
