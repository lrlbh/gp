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

# 获取股票名称
start = time.time()
股票列表 = gp.gp.get_股票列表(False)
股票列表 = dict(zip(股票列表["ts_code"], 股票列表["name"]))
print(time.time() - start)

df = df_list["002321.SZ"]
t_this = df["tz_等购买力"].iloc[-1]
t_min = df["tz_等购买力"].min()
t_avg = df["tz_等购买力"].mean()


print(t_this, t_min, t_avg)


df = df_list["002321.SZ"]
t_this = df["tz_等地位"].iloc[-1]
t_min = df["tz_等地位"].min()
t_avg = df["tz_等地位"].mean()


print(t_this, t_min, t_avg)
