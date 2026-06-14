from audioop import avg
import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp.gdp
import gp.m2
import gp.gp
from datetime import datetime
import gp.史低股
import gp.tz
import gp.r人口

plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False
# gp.gp.更新()
# 1 / 0

# gp.r人口.get_人口定基增长率()
# 1 / 0

T = gp.tz.get_等地位货币通胀()
1 / 0

T = gp.tz.get_等购买力通胀()
1 / 0

T = gp.gdp.get_gdp定基增长倍率()
print(T)
1 / 0

T = gp.m2.get_m2定基增长率()
print(T)
1 / 0

开始时间 = "2004"


# 获取通胀数据
gdp = gp.gdp.get_gdp_补偿(开始时间)
m2 = gp.m2.get_m2_补偿(开始时间)
# tz = {key: (1 + m2[key]) / (1 + gdp[key]) for key in m2}
tz = {key: (m2[key] / gdp[key]) for key in m2}
print(tz)
x_time = [datetime.strptime(date, "%Y%m%d") for date in tz.keys()]
plt.plot(x_time, tz.values(), color="red", label="货币贬值趋势")
x_time = [datetime.strptime(date, "%Y%m%d") for date in gdp.keys()]
plt.plot(x_time, gdp.values(), color="blue", label="GDP增长趋势")
x_time = [datetime.strptime(date, "%Y%m%d") for date in m2.keys()]
plt.plot(x_time, m2.values(), color="green", label="M2增长趋势")
plt.legend()
plt.show()

上市第一天 = "20040101"
基准贬值 = tz[上市第一天]
for key in tz:
    tz[key] /= 基准贬值


tz = {key: value for key, value in tz.items() if key >= 上市第一天}
gdp = {key: value for key, value in gdp.items() if key >= 上市第一天}
m2 = {key: value for key, value in m2.items() if key >= 上市第一天}

x_time = [datetime.strptime(date, "%Y%m%d") for date in tz.keys()]
plt.plot(x_time, tz.values(), color="red", label="货币贬值趋势")
x_time = [datetime.strptime(date, "%Y%m%d") for date in gdp.keys()]
plt.plot(x_time, gdp.values(), color="blue", label="GDP增长趋势")
x_time = [datetime.strptime(date, "%Y%m%d") for date in m2.keys()]
plt.plot(x_time, m2.values(), color="green", label="M2增长趋势")
plt.legend()
plt.show()


# start = time.time()
# gp_list = gp.gp.get_all_股票数据(开始时间)
# print(time.time() - start)

# start = time.time()
# hfq_list = gp.gp.get_后复权数据(gp_list)
# print(time.time() - start)

# start = time.time()
# tz_list = gp.gp.get_通胀修复数据(hfq_list)
# print(time.time() - start)

# print(tz_list)


# print(
#     f"代码: {code} 平均值: {股票平均值} 最小值: {股票最小值} 当前值: {股票当前值}"
# )
