import math
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
import no_git

# gp.gp.更新()
# 1 / 0

公司信息 = gp.gp.get_股票列表(False)


date = 20260615
df_list = gp.gp.get_all_股票数据(date)


result = {}
for code in no_git.no_code:
    # 获取对应股票
    df = df_list[code]

    # 计算盘中高低点的后复权数据
    复权因子 = (
        df["pre_close"].iloc[0]
        * (df["close"] / df["pre_close"]).cumprod()
        / df["close"]
    )
    # if code == "603102.SH":
    #     print(复权因子)

    # 生成盘中高地的后复权数据
    df["high_hfq"] = df["high"] * 复权因子
    df["low_hfq"] = df["low"] * 复权因子
    df["close_hfq"] = df["close"] * 复权因子

    # 历史收盘价，最低和最高点
    min_date = df["close_hfq"].idxmin()
    min_value = df["close_hfq"].min()
    max_value = df.loc[df.index >= min_date, "close_hfq"].max()

    # 历史盘中价，最低和最高点
    min_date_2 = df["low_hfq"].idxmin()
    min_value_2 = df["low_hfq"].min()
    max_value_2 = df.loc[df.index > min_date_2, "high_hfq"].max()

    # 当天收盘价格涨幅
    min_date_3 = df["hfq"].idxmin()
    min_value_3 = df["hfq"].min()
    max_value_3 = df["hfq"].iloc[-1]

    # 当天盘中价格涨幅
    min_date_4 = df["low_hfq"].idxmin()
    min_value_4 = df["low_hfq"].min()
    max_value_4 = df["close_hfq"].iloc[-1]

    result[code] = {
        "收盘max": max_value,
        "收盘min": min_value,
        "历史收盘涨幅": max_value / min_value,
        "盘中max": max_value_2,
        "盘中min": min_value_2,
        "历史盘中涨幅": max_value_2 / min_value_2,
        "当天收盘max": max_value_3,
        "当天收盘min": min_value_3,
        "当天收盘涨幅": max_value_3 / min_value_3,
        "当天盘中max": max_value_4,
        "当天盘中min": min_value_4,
        "当天盘中涨幅": max_value_4 / min_value_4,
    }


file_name = "test/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"


def 写入排序结果(file_name, result, 排序字段, 涨幅筛选):

    排序结果 = sorted(
        result.items(),
        key=lambda x: x[1][排序字段],
        reverse=True,
    )

    with open(
        file_name,
        "a",
        encoding="utf-8",
    ) as f:
        f.write(f"\n\n\n{排序字段}\n")

        for key, value in 排序结果:
            if value[排序字段] < 涨幅筛选:
                continue

            this_公司信息 = 公司信息.loc[公司信息["ts_code"] == key].iloc[0]
            f.write(f" {key}\t{this_公司信息['name']} -->  {value[排序字段]:.3f}\n")


写入排序结果(file_name, result, "当天收盘涨幅", 1.4)
写入排序结果(file_name, result, "当天盘中涨幅", 1.4)
写入排序结果(file_name, result, "历史收盘涨幅", 1.4)
写入排序结果(file_name, result, "历史盘中涨幅", 1.4)
