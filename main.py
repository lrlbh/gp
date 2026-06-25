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
from collections import defaultdict

# tz2.index = pd.to_datetime(tz2.index, format="%Y%m%d")
# plt.plot(tz2["temp_定基"], color="red", label="后复权", linestyle="--")
plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False
# gp.gp.更新()
# 1 / 0

date = 19900201


# 获取完整股票数据
df_list = gp.gp.get_all_股票数据(date)

# 获取股票名称
股票列表 = gp.gp.get_股票列表(False)
股票列表 = dict(zip(股票列表["ts_code"], 股票列表["name"]))

# 数据截止到某一天
# for key in df_list:
#     df_list[key] = df_list[key][df_list[key].index <= 20260617]


def test(df_list, 列名, 忽略code=[], 忽略均值=2.7, 低价阈值=1.05):

    # 筛选史低股票
    df_筛选后 = {
        key: value
        for key, value in df_list.items()
        if not value.empty
        # 定义变量
        for code, this, t_min, t_max, t_avg in [
            (
                value["ts_code"].iloc[-1],
                value[列名].iloc[-1],
                value[列名].min(),
                value[列名].max(),
                value[列名].mean(),
            )
        ]
        # 筛选条件
        # if this * 低价阈值 > t_max
        if this < t_min * 低价阈值
        and t_avg / t_min > 忽略均值
        and code not in 忽略code  # 为了自动换行
    }

    # 打开文件
    f = open(
        "test/" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".txt",
        "a",
        encoding="utf-8",
    )

    # 写入基础信息
    f.write(
        f"{列名},史低股数量: {len(df_筛选后)}\t起点日期: {date}\t史地阈值: {低价阈值} 平均值阈值: {忽略均值}:\n"
    )

    # 写入列名
    f.write(
        "\t".join(
            [
                "公司名称",
                "股票代码",
                "伪上市时间",
                # "当前价",
                # "最低价",
                # "平均价",
                "实价",
                "理论实价",
                "当前",
                "平均",
            ]
        )
        + "\n"
    )

    for key, df in sorted(
        df_筛选后.items(),
        key=lambda x: x[1][列名].mean() / x[1][列名].min(),
        reverse=True,
    ):
        df = df_筛选后[key]
        最低价 = df[列名].min()
        平均价 = df[列名].mean()
        当前价 = df[列名].iloc[-1]
        上市时间 = df.index[0]
        公司名 = 股票列表[key]
        公司名 = 公司名 + "  " if len(公司名) <= 3 else 公司名
        股票代码 = key
        实际价格 = df["close"].iloc[-1]
        历史平均值倍率 = 平均价 / 最低价
        价格修正 = 历史平均值倍率 / 3
        if 历史平均值倍率 < 3:
            购入金额 = 3000 * 价格修正 * 价格修正
        elif 历史平均值倍率 > 4:
            购入金额 = 3000 * 1.33
        else:
            购入金额 = 3000 * 价格修正

        if 公司名 == "中国铁物":
            print(当前价 / 最低价)
            print(当前价, 最低价)

        t_str = (
            f"{公司名}\t"
            + f"{股票代码}\t"
            + f"{上市时间}\t"
            # + f"{t_this:.2f}\t"
            # + f"{t_min:.2f}\t"
            # + f"{avg:.2f}\t"
            + f"{实际价格:.2f}\t"
            + f"{实际价格 / (当前价 / 最低价):.3f}\t"
            + f"{当前价 / 最低价:.2f}\t"
            + f"{历史平均值倍率:.2f}\t"
            + f"{购入金额:.0f}"
            + "\n"
        )

        f.write(t_str)

    f.write("\n\n\n")
    f.close()


import no_git

test(df_list, "tz_等购买力", 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.10, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.15, 忽略均值=1, 忽略code=no_git.no_code)
test(df_list, "hfq")
# test(df_list, "tz_等地位")
