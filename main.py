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

date = 20040101

# 获取完整股票数据
start = time.time()
df_list = gp.gp.get_all_股票数据(date)
print(time.time() - start)

# 筛选股票
df_list = {
    key: value
    for key, value in df_list.items()
    # 定义变量
    for this, t_min, t_avg in [
        (
            value["tz_等地位"].iloc[-1],
            value["tz_等地位"].min(),
            value["tz_等地位"].mean(),
        )
    ]
    # 筛选条件
    if this < t_min * 1.05 and this * 9 < t_avg
}

for key in df_list:
    print(key)

1 / 0
