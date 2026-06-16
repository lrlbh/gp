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


def test(df_list, 列名):
    t2 = 20  # 从平均值多少倍开始筛选
    while True:
        df_筛选后 = {
            key: value
            for key, value in df_list.items()
            # 定义变量
            for this, t_min, t_avg in [
                (
                    value[列名].iloc[-1],
                    value[列名].min(),
                    value[列名].mean(),
                )
            ]
            # 筛选条件
            if this < t_min * 1.05 and this * t2 < t_avg
        }
        if len(df_筛选后) >= 6:
            break

        if t2 <= 5:
            t2 -= 0.1
        else:
            t2 -= 1

    f = open(
        "test/" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".txt",
        "a",
        encoding="utf-8",
    )
    f.write(f"{列名}\t起点日期: {date} \n")
    f.write("公司名称\t股票代码\t伪上市时间\t当前价\t最低价\t平均价\t当前\t低于平均\n")
    for key in df_筛选后:
        t_min = df_筛选后[key][列名].min()
        avg = df_筛选后[key][列名].mean()
        t_this = df_筛选后[key][列名].iloc[-1]
        伪上市时间 = df_筛选后[key].index[0]
        name = 股票列表[key]
        code = key
        if len(name) <= 3:
            name += "  "

        f.write(
            f"{name}\t{code}\t{伪上市时间}\t{t_this:.2f}\t{t_min:.2f}\t{avg:.2f}\t{t_this / t_min:.2f}\t{avg / t_this:.2f}\n"
        )
    f.write("\n\n\n")
    f.close()


test(df_list, "tz_等购买力")
print("----------------------")
test(df_list, "tz_等地位")
