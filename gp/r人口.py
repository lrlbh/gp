import pandas as pd
from datetime import datetime
import gp.pub
from functools import lru_cache


@lru_cache(maxsize=None)
def get_人口数据():
    df = pd.read_csv(gp.pub.人口_path, encoding="utf_8_sig")

    # 预测两年就够了，人口数据只会滞后一年多
    for _ in range(2):
        # 最近3年人口平均增速预测新的一年
        temp_df = df[df["数据类型"].isin(["年度年末", "预测数据"])]

        t = sum(temp_df.tail(3)["人口数量"])
        人口基准 = temp_df.iloc[-4]["人口数量"]
        最后日期 = temp_df.iloc[-1]["date"] + 10000
        最后人口 = temp_df.iloc[-1]["人口数量"]

        下一年人口 = 最后人口 * (t / 人口基准 / 3)

        new_row = {"date": 最后日期, "人口数量": 下一年人口, "数据类型": "预测数据"}

        # 直接把新数据怼进 df
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df["date"] = df["date"].astype(str)
    return df


@lru_cache(maxsize=None)
def __init_人口增长(开始日期="1989"):

    df = get_人口数据()

    # 截断早期数据
    df = df[df["date"] > 开始日期].copy()

    # 获取基值
    基值 = df[df["date"] == 开始日期 + "1231"].人口数量.item()

    # 计算定基增长率
    df["定基增长率"] = df["人口数量"] / 基值

    # 重采样到天
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df.set_index("date", inplace=True)
    df = df.resample("D").asfreq()

    # 线性插值
    df["定基增长率"] = df["定基增长率"].interpolate(method="linear")

    # 统一时间格式
    df.index = df.index.strftime("%Y%m%d").astype(int)

    # 截断多余数据
    df = df.loc[: int(datetime.now().strftime("%Y%m%d"))]

    return df


def get_人口定基增长率(开始日期=20040101):
    df = __init_人口增长()

    基准值 = df.loc[开始日期, "定基增长率"]

    df["temp_定基"] = df["定基增长率"] / 基准值

    # print(df.loc[开始日期:])
    return df.loc[开始日期:]
