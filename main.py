import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp
from datetime import datetime


def show_gdp_插值():
    df = gp.get_gdp()
    # df = df[df["quarter"] < "2000"]
    df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)
    df = df.sort_values(by="quarter", ascending=True).reset_index(drop=True)

    df_full = gp.get_gdp_插值()
    # df_full = df_full[df_full["quarter"] < "2000"]
    df_full["quarter"] = pd.to_datetime(df_full["quarter"]) + pd.offsets.QuarterEnd(0)
    df_full = df_full.sort_values(by="quarter", ascending=True).reset_index(drop=True)

    plt.plot(df["quarter"], df["gdp"], zorder=3)
    plt.plot(df_full["quarter"], df_full["gdp"], zorder=2)

    plt.show()


# show_gdp_插值()


def 同比补偿(开始日期="2000"):

    # 返回值
    ret = {}

    # 获取gdp数据
    df = gp.get_gdp_插值()

    # # 前一年的 Q1~Q4 GDP数据
    # 季度基值 = {"Q1": None, "Q2": None, "Q3": None, "Q4": None}
    # for key in 季度基值:
    #     季度基值[key] = df[df["quarter"] == str(int(开始日期) - 1) + key].gdp.item()

    # # 对比前一年的，同比增长数据
    # 总年数 = int(datetime.now().strftime("%Y")) - int(开始日期) + 1
    # for i in range(总年数):
    #     当前年 = str(int(开始日期) + i)
    #     for key in 季度基值:
    #         本季gdp = df.loc[df["quarter"] == 当前年 + key, "gdp"].values[0]
    #         本季gdp = (本季gdp - 季度基值[key]) / 季度基值[key]  # 增长百分比
    #         ret[当前年 + key] = 本季gdp
    #         # if key == "Q1":
    #         #     print(本季gdp)


    # ==================== 修改开始 ====================
    # 1. 先在局部将 GDP 累计值 还原为 真正的单季当季值 (YTD -> Quarterly)
    # 确保 df 是按时间正序排列的，方便差分
    df_sorted = df.sort_values("quarter").reset_index(drop=True)
    df_sorted["year"] = df_sorted["quarter"].str[:4]
    
    # 利用 groupby(year) 并在组内差分：如果是Q1就保持原样，Q2~Q4减去前一季
    # 这样能完美处理每年一季度的特殊情况
    df_sorted["gdp_diff"] = df_sorted.groupby("year")["gdp"].diff().fillna(df_sorted["gdp"])
    
    # 建立一个 季度->当季GDP 的映射字典，方便后续极速查询
    gdp_map = dict(zip(df_sorted["quarter"], df_sorted["gdp_diff"]))

    # 2. 获取基准年（前一年）的 Q1~Q4 当季 GDP 基值
    季度基值 = {"Q1": None, "Q2": None, "Q3": None, "Q4": None}
    for key in 季度基值:
        基准季度 = str(int(开始日期) - 1) + key
        if 基准季度 not in gdp_map:
            raise ValueError(f"数据源中缺少基准季度: {基准季度}")
        季度基值[key] = gdp_map[基准季度]

    # 3. 对比基准年，计算定基增长数据
    总年数 = int(datetime.now().strftime("%Y")) - int(开始日期) + 1
    for i in range(总年数):
        当前年 = str(int(开始日期) + i)
        for key in 季度基值:
            当前季度 = 当前年 + key
            if 当前季度 not in gdp_map:
                continue  # 容错：如果最新年份的某些季度还没公布，直接跳过
                
            本季gdp_当季 = gdp_map[当前季度]
            
            # 使用还原后的【当季值】对比基准年的【当季值】计算增长百分比
            本季gdp_增长率 = (本季gdp_当季 - 季度基值[key]) / 季度基值[key]
            ret[当前季度] = 本季gdp_增长率
            # if key == "Q1":
            #     print(本季gdp_增长率)
    # ==================== 修改结束 ====================

    # 同比增长数据，插值到每一天
    # 同比增长数据，插值到每一天
    # 1. 准备季度数据
    df = pd.DataFrame(list(ret.items()), columns=["quarter", "value"])
    df["quarter"] = pd.PeriodIndex(df["quarter"], freq="Q")
    df["date"] = (
        df["quarter"].dt.to_timestamp(how="end").dt.normalize()
    )  # 关键：normalize 去掉时间部分
    df = df.sort_values("date").reset_index(drop=True)

    # 2. 生成日度范围：2000-01-01 到 2026-12-31
    end_time = datetime.now().strftime("%Y") + "-12-31"
    daily_dates = pd.date_range(start=f"{开始日期}-01-01", end=end_time, freq="D")

    # 3. 合并并插值
    df_daily = pd.DataFrame({"date": daily_dates})
    df_daily = df_daily.merge(df[["date", "value"]], on="date", how="left")

    # 线性插值（季度末之间）
    df_daily["ret_daily"] = df_daily["value"].interpolate(method="linear")

    # 4. 处理边界：2000-01-01 到 2000-03-31 没有前一个季度，用 bfill 填充
    df_daily["ret_daily"] = df_daily["ret_daily"].bfill()

    # 清理
    df_daily = df_daily.drop(columns=["value"])

    # # 在图形中，对比插值前后
    # # 在图形中，对比插值前后
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    new_dict_end = {pd.Period(k, freq="Q").end_time: v for k, v in ret.items()}
    plt.plot(df_daily["date"], df_daily["ret_daily"], zorder=2)
    plt.plot(new_dict_end.keys(), new_dict_end.values(), zorder=3)
    plt.show()

    return df_daily


同比补偿()


# gp.更新()
