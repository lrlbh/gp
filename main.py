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

plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False
# gp.gp.更新()
# 1 / 0


def 归一化(input_dict):
    """
    对输入字典的 values 进行原地 Min-Max 归一化（无返回值，直接修改原字典）。
    适用于将数据缩放到 0~1 之间以方便用 plt 显示。
    """
    if not input_dict:
        return

    values = list(input_dict.values())
    v_min = min(values)
    v_max = max(values)
    v_range = v_max - v_min

    # 如果字典内所有值都相等，统一归一化为 1.0（或者 0.0，视你图像显示的需要而定）
    if v_range == 0:
        for k in input_dict.keys():
            input_dict[k] = 1.0
        return

    # 直接在原字典上修改 values
    for k in input_dict.keys():
        input_dict[k] = (input_dict[k] - v_min) / v_range


开始时间 = "2004"

# 获取通胀数据
gdp = gp.gdp.get_gdp_补偿(开始时间)
m2 = gp.m2.get_m2_补偿(开始时间)
货币贬值 = {key: m2[key] - gdp[key] for key in m2}
# print(dict(list(货币贬值.items())[:-10]))
# x_time = [datetime.strptime(date, "%Y%m%d") for date in 货币贬值.keys()]
# plt.plot(x_time, 货币贬值.values(), color="red", label="货币贬值趋势")
# x_time = [datetime.strptime(date, "%Y%m%d") for date in gdp.keys()]
# plt.plot(x_time, gdp.values(), color="blue", label="GDP增长趋势")
# x_time = [datetime.strptime(date, "%Y%m%d") for date in m2.keys()]
# plt.plot(x_time, m2.values(), color="green", label="M2增长趋势")
# plt.legend()
# plt.show()


# 获取股票列表
min_code_list = []
异常_min_code_list = []
code_list = gp.gp.get_股票列表(True)
for row in code_list.itertuples():
    code = row.ts_code

    # 部分股票没有数据，跳过
    # 部分股票代码,被回收复用,TS开头
    if code.startswith("TS"):
        continue

    if code.startswith("T"):
        continue

    if code.endswith("BJ"):
        continue

    if row.list_status == "D":
        # 退市列表.append(code)
        continue
    if row.list_status == "P":
        # 暂停上市列表.append(code)
        continue
    if row.list_status == "G":
        # 未交易列表.append(code)
        continue

    # 获取后复权股票数据
    hfq = gp.gp.后复权数据(code, 开始时间)
    tz = hfq.copy()
    # 修复通胀
    上市第一天 = min(tz.keys())
    for key in tz:
        区间贬值 = 货币贬值[key] - 货币贬值[上市第一天]
        tz[key] /= 1 + 货币贬值[key]

    tz_list = list(tz.values())
    股票平均值 = sum(tz_list) / len(tz_list)
    股票当前值 = tz_list[-1]
    股票最小值 = min(tz_list)
    # print(
    #     f"代码: {code} 平均值: {股票平均值} 最小值: {股票最小值} 当前值: {股票当前值}"
    # )

    if 股票当前值 <= 股票最小值 * 1.01 and 股票当前值 * 9 <= 股票平均值:
        if row.name.startswith(("S", "s", "*", "退")):
            异常_min_code_list.append(code + "-->" + row.name)
        else:
            min_code_list.append(code + "-->" + row.name)

            # print(异常_min_code_list)
            # print(min_code_list)
            # print(len(min_code_list))
            # 归一化(hfq)
            # 归一化(tz)
            plt.title(row.name)
            x_time = [datetime.strptime(date, "%Y%m%d") for date in hfq.keys()]
            plt.plot(x_time, hfq.values(), color="green", label="股价")
            x_time = [datetime.strptime(date, "%Y%m%d") for date in tz.keys()]
            plt.plot(x_time, tz.values(), color="red", label="股价通胀修复")
            plt.legend()
            plt.show()
