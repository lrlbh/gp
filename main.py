import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import akshare as ak
import gp


def 同比补偿(df_in):
    # 开始日期 = str(int(开始日期) - 1)
    df_in = df_in[df_in["quarter"] > '1990']  # 2000 年后

    # 时间升序
    df = df_in.sort_values(by="quarter", ascending=True).reset_index(drop=True)

    # 数据.开始年、结束年、总年份
    start_time = int(df["quarter"].iloc[0][:-2])
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

    # 获取每个分组的数量
    df_q1 = df_gro.get_group("Q1").reset_index(drop=True)
    df_q2 = df_gro.get_group("Q2").reset_index(drop=True)
    df_q3 = df_gro.get_group("Q3").reset_index(drop=True)
    df_q4 = df_gro.get_group("Q4").reset_index(drop=True)


    增长系数 = []
    old_row = None
    for index, row in df_q1.iterrows():
        if index == 0:
            old_row = row
            continue

        增长系数.append(row.gdp / old_row.gdp)
        old_row = row
    增长系数 = sum(增长系数) / len(增长系数)

    print(增长系数)
    print((df_q1['gdp'] / df_q1['gdp'].shift(1)).mean())
    

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


df = gp.get_gdp()

同比补偿(df)


# df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)  # 季度转日期
# plt.plot(df["quarter"], gdp增长)
# plt.grid(True)
# plt.show()

# gp.更新()
