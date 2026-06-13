import os.path
import time
import os
from pathlib import Path
import pandas as pd
import tl
import tl.dir
from datetime import datetime
import gp.pub
import numpy as np
import math
from functools import lru_cache
from datetime import timedelta


@lru_cache(maxsize=None)
def get_m2(更新=False, 更新间隔S=60 * 60 * 24):

    # 是否需要更新
    if os.path.exists(gp.pub.m2_path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(gp.pub.m2_path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(gp.pub.m2_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: M2列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(gp.pub.m2_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: M2列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新M2 -> {gp.pub.m2_path}")
    df = gp.pub.pro.cn_m(
        **{"m": "", "start_m": "", "end_m": "", "limit": "", "offset": ""},
        fields=[
            "month",
            "m0",
            "m0_yoy",
            "m0_mom",
            "m1",
            "m1_yoy",
            "m1_mom",
            "m2",
            "m2_yoy",
            "m2_mom",
        ],
    )

    # 写入到文件
    tl.dir.ensure_path_exists(gp.pub.m2_path)
    df.to_csv(gp.pub.m2_path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {m2_path}")
    if len(df) >= 5999:
        print("WAR: M2数据可能溢出了")

    return df


@lru_cache(maxsize=None)
def get_m2_插值():
    df = get_m2(True)
    df["year"] = df["month"] // 100
    df["mon"] = df["month"] % 100

    df = df.sort_values("month").reset_index(drop=True)
    df["m2_插值标记"] = pd.Series(dtype="object")

    # 1. 补齐1990-1992年：用12月m2/m1比值
    for y in [1990, 1991, 1992]:
        dec = df[(df["year"] == y) & (df["mon"] == 12)]
        if len(dec) > 0 and pd.notna(dec["m2"].values[0]):
            ratio = dec["m2"].values[0] / dec["m1"].values[0]
            mask = (df["year"] == y) & (df["m2"].isnull())
            df.loc[mask, "m2"] = df.loc[mask, "m1"] * ratio
            df.loc[mask, "m2_插值标记"] = f"{y}年m2/m1比值"

    # =========================================================================
    # 2. 预测未来12个月：改用前三年同期的 m2_yoy 均值进行预测
    # =========================================================================
    # 获取当前数据集中最新的那一行（作为预测的起点）
    latest_row = df[df["m2"].notnull()].sort_values("month").iloc[-1]
    start_year = int(latest_row["year"])
    start_mon = int(latest_row["mon"])

    # 动态生成未来12个月的年份和月份
    future_months = []
    curr_y, curr_m = start_year, start_mon
    for _ in range(12):
        curr_m += 1
        if curr_m > 12:
            curr_m = 1
            curr_y += 1
        future_months.append((curr_y, curr_m))

    # 逐月循环预测（因为后面的预测可能会依赖前面刚预测出来的值作为基数）
    for pred_year, pred_mon in future_months:
        # 寻找前三年的同期同比数据 (t-1, t-2, t-3)
        past_yoys = []
        for lag in [1, 2, 3]:
            target_year = pred_year - lag
            # 从当前已经扩充的 df 中找过去的数据
            past_row = df[(df["year"] == target_year) & (df["mon"] == pred_mon)]
            if len(past_row) > 0 and pd.notna(past_row["m2_yoy"].values[0]):
                past_yoys.append(past_row["m2_yoy"].values[0])

        # 如果前三年数据不全，降级使用能找到的均值；如果完全没有，设定一个兜底值（如 7.0）
        pred_yoy = np.mean(past_yoys) if len(past_yoys) > 0 else 7.0

        # 寻找前一年的 M2 真实值/预测值作为基数
        base_row = df[(df["year"] == (pred_year - 1)) & (df["mon"] == pred_mon)]

        if len(base_row) > 0 and pd.notna(base_row["m2"].values[0]):
            base_m2 = base_row["m2"].values[0]
            pred_m2 = base_m2 * (1 + pred_yoy / 100)
        else:
            # 极端情况：如果连去年同期的基数都没有，跳过或设为 NaN
            continue

        new_row = pd.DataFrame(
            {
                "month": [pred_year * 100 + pred_mon],
                "year": [pred_year],
                "mon": [pred_mon],
                "m2": [pred_m2],
                "m2_yoy": [pred_yoy],
                "m2_插值标记": [f"{pred_year}预测(前3年均值)"],
            }
        )
        df = pd.concat([df, new_row], ignore_index=True)

    # =========================================================================

    # 3. 重算mom/yoy
    df = df.sort_values("month").reset_index(drop=True)
    df["m2_mom"] = df["m2"].pct_change() * 100

    df["m2_yoy"] = np.nan
    for i in range(len(df)):
        if pd.notna(df.loc[i, "m2"]):
            ly = (df.loc[i, "year"] - 1) * 100 + df.loc[i, "mon"]
            ly_row = df[df["month"] == ly]
            if len(ly_row) > 0 and pd.notna(ly_row["m2"].values[0]):
                df.loc[i, "m2_yoy"] = round(
                    (df.loc[i, "m2"] / ly_row["m2"].values[0] - 1) * 100, 1
                )

    df["m2_插值标记"] = df["m2_插值标记"].fillna("原始")
    df["month"] = df["month"].astype(str)  # 日期转字符串
    print(df)
    return df


@lru_cache(maxsize=None)
def get_m2_货币补偿(开始日期="20000101"):
    ret = {}

    df_m2 = get_m2_插值()

    # 通过month列生成新列date，month+本月最后日期 == date
    df_m2["date"] = pd.to_datetime(
        df_m2["month"].astype(str) + "01"
    ) + pd.offsets.MonthEnd(0)

    # 设置date为索引列
    df_m2 = df_m2.set_index("date")

    # 今天的日期+一个月
    结束日期 = (datetime.today() + timedelta(days=31)).strftime("%Y%m%d")

    # 生成按天递增的日期数据
    all_days = pd.date_range(start=开始日期, end=结束日期, freq="D")
    print(all_days)

    # 生成PD数据结构 2026-04-05 NaN
    daily_df = pd.DataFrame(index=all_days).join(df_m2["m2"])
    print(daily_df)

    # 执行线性插值，让 M2 每天平滑地“均匀增长”
    daily_df["m2"] = daily_df["m2"].interpolate(method="linear")
    # 假设第一个月不存在通胀，少算最多一个月的通胀
    daily_df["m2"] = daily_df["m2"].bfill()

    # 2. 计算基于开始日期的“补偿增幅系数”
    base_m2 = daily_df.iloc[0]["m2"]
    daily_df["补偿系数"] = daily_df["m2"] / base_m2

    # 3. 填充到 ret 字典
    ret = {k.strftime("%Y%m%d"): round(v, 6) for k, v in daily_df["补偿系数"].items()}
    print(ret)
    #  '20260711': 30.165513 日期和货币增长了多少倍
    return ret
