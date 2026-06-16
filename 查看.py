import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp.tz.gdp
import gp.tz.m2
import gp.gp
from datetime import datetime
import gp.tz.tz
import gp.tz.r人口

# tz2.index = pd.to_datetime(tz2.index, format="%Y%m%d")
# plt.plot(tz2["temp_定基"], color="red", label="后复权", linestyle="--")
plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False
# gp.gp.更新()
# 1 / 0

date = 19900201


# 获取完整股票数据
start = time.time()
df_list = gp.gp.get_all_股票数据(date)
print(time.time() - start)

# 1. 确保索引为日期
df_list["600613.SH"].index = pd.to_datetime(df_list["600613.SH"].index, format="%Y%m%d")
df = df_list["600613.SH"]

plt.figure(figsize=(10, 5))
plt.plot(df["hfq"], color="red", label="后复权 (0-1)")
plt.plot(df["tz_等购买力"], color="blue", label="tz_等购买力 (0-1)")
plt.plot(df["tz_等地位"], color="g", label="tz_等地位 (0-1)")

plt.axhline(
    y=df["hfq"].mean(),
    color="red",
    ls="--",
    alpha=0.6,
    # label=f"后复权 AVG: {hfq_avg:.2f}",
)
plt.axhline(
    y=df["tz_等购买力"].mean(),
    color="blue",
    ls="--",
    alpha=0.6,
    # label=f"tz_等购买力 AVG: {gml_avg:.2f}",
)
plt.axhline(
    y=df["tz_等地位"].mean(),
    color="g",
    ls="--",
    alpha=0.6,
    # label=f"tz_等地位 AVG: {ddw_avg:.2f}",
)

plt.title("3条走线归一化对比 (Min-Max 0-1)")
plt.legend()
plt.grid(True)
plt.show()
