import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp
from datetime import datetime


def 同比补偿(开始日期="1992"):
    df_full = gp.get_gdp插值()
    df = gp.get_gdp()

    df_full = df_full[df_full["quarter"] < "2000"]
    df_full["quarter"] = pd.to_datetime(df_full["quarter"]) + pd.offsets.QuarterEnd(0)
    df_full = df_full.sort_values(by="quarter", ascending=True).reset_index(drop=True)
    plt.plot(df_full["quarter"], df_full["gdp"])

    df = df[df["quarter"] < "2000"]
    df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)
    df = df.sort_values(by="quarter", ascending=True).reset_index(drop=True)
    plt.plot(df["quarter"], df["gdp"])
    plt.show()

    return
    # 返回值
    ret = {}
    ret[开始日期 + "0101"] = None
    ret[datetime.now().strftime("%Y%m%d")] = None

    q1_基值 = df_in[df_in["quarter"] == 开始日期 + "Q1"].gdp.item()
    print(q1_基值)

    q2_基值 = 0
    q3_基值 = 0
    q4_基值 = 0

    return
    # 筛选数据开始年
    df = df_in[df_in["quarter"] > str(int(开始日期) - 1)]

    # 时间升序
    df = df.sort_values(by="quarter", ascending=True).reset_index(drop=True)

    # 数据.开始年、结束年、总年份
    start_time = 开始日期
    end_time = int(df["quarter"].iloc[-1][:-2])
    time_num = end_time - start_time + 1

    # 用最后两个字符生成一个新列
    df["q_label"] = df["quarter"].str[-2:]

    # 通过新列分组
    df_gro = df.groupby("q_label")

    # 校验分组数量
    if df_gro.ngroups != 4:
        raise Exception("季度分组后不等于4!!!")

    # print(df_fro.size()) # 每个分组的数据量

    # 获取每个分组的数据
    df_q1 = df_gro.get_group("Q1").reset_index(drop=True)
    df_q2 = df_gro.get_group("Q2").reset_index(drop=True)
    df_q3 = df_gro.get_group("Q3").reset_index(drop=True)
    df_q4 = df_gro.get_group("Q4").reset_index(drop=True)

    # 每个季度的平均增速
    df_q1_增长 = ((df_q1["gdp"] - df_q1["gdp"].shift(1)) / df_q1["gdp"].shift(1)).mean()
    df_q2_增长 = ((df_q2["gdp"] - df_q2["gdp"].shift(1)) / df_q2["gdp"].shift(1)).mean()
    df_q3_增长 = ((df_q3["gdp"] - df_q3["gdp"].shift(1)) / df_q3["gdp"].shift(1)).mean()
    df_q4_增长 = ((df_q4["gdp"] - df_q4["gdp"].shift(1)) / df_q4["gdp"].shift(1)).mean()
    # df_q1_增长 = (df_q1["gdp"] / df_q1["gdp"].shift(1)).mean()
    # df_q2_增长 = (df_q2["gdp"] / df_q2["gdp"].shift(1)).mean()
    # df_q3_增长 = (df_q3["gdp"] / df_q3["gdp"].shift(1)).mean()
    # df_q4_增长 = (df_q4["gdp"] / df_q4["gdp"].shift(1)).mean()

    print(df_q1_增长)
    print(df_q2_增长)
    print(df_q3_增长)
    print(df_q4_增长)

    # for i in range(time_num):
    #     if df_q1["quarter"].str.contains(str(start_time + i)).any():
    #         print(start_time + i)

    print(len(df_q1))
    print(len(df_q2))
    print(len(df_q3))
    print(len(df_q4))

    # for name, df_qx in df_gro:
    #     print(f"=== 当前正在访问的组是: {name} ===")
    #     print(df_qx)  # 在这里对这一个季度的 DataFrame 做你想要的计算


同比补偿()


# df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)  # 季度转日期
# plt.plot(df["quarter"], gdp增长)
# plt.grid(True)
# plt.show()

# gp.更新()
