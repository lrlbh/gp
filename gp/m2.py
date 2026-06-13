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

    # 2. 预测2026年5-12月
    y2026 = df[df["year"] == 2026].copy()
    y2025 = df[df["year"] == 2025].copy()

    last_yoy = y2026[y2026["m2_yoy"].notnull()]["m2_yoy"].iloc[-1]
    for i, mon in enumerate(range(5, 13)):
        pred_yoy = max(7.0, last_yoy - 0.08 * (i + 1))
        base_m2 = y2025[y2025["mon"] == mon]["m2"].values[0]
        pred_m2 = base_m2 * (1 + pred_yoy / 100)

        new_row = pd.DataFrame(
            {
                "month": [2026 * 100 + mon],
                "year": [2026],
                "mon": [mon],
                "m2": [pred_m2],
                "m2_yoy": [pred_yoy],
                "m2_插值标记": ["2026预测"],
            }
        )
        df = pd.concat([df, new_row], ignore_index=True)

    # 重算mom/yoy
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
    return df


# 原始数据插值前后
# def show_m2_插值():
#     df = gp.get_m2()
#     df_full = gp.get_m2_插值()
#     plt.plot(df["month"], df["m2"], zorder=3)
#     plt.plot(df_full["month"], df_full["m2"], zorder=2)
#     plt.show()
# show_m2_插值()


def get_m2_补偿(开始日期="2000"):

    # 返回值
    ret = {}

    # 获取gdp数据
    df = get_m2_插值()
    df["month"] = df["month"].astype(str)  # 日期转字符串

    # 前一个月数据
    基值m2 = df[df["month"] == str(int(开始日期) - 1) + "12"].m2.item()
    if math.isnan(基值m2):
        raise Exception("还没有生成早期M2数据")

    # 对比前一年的，同比增长数据
    总月数 = (int(datetime.now().strftime("%Y")) - int(开始日期) + 1) * 12
    for i in range(总月数):
        当前年月 = f"{int(开始日期) + (i // 12)}{(i % 12) + 1:02d}"
        当前月的m2 = df[df["month"] == 当前年月].m2.item()
        ret[当前年月] = (当前月的m2 - 基值m2) / 基值m2
        # print(f"{当前年月} {(当前月的m2 - 基值m2) / 基值m2}")
    # print(ret)

    # 2. 将数据转换为 pandas 的 DataFrame
    # 将 'YYYYMM' 格式的键解析为该月的最后一天（或第一天，这里选最后一天作为锚定点）
    df_monthly = pd.DataFrame(list(ret.items()), columns=["YearMonth", "Value"])
    df_monthly["Date"] = pd.to_datetime(
        df_monthly["YearMonth"] + "01", format="%Y%m%d"
    ) + pd.offsets.MonthEnd(0)
    df_monthly.set_index("Date", inplace=True)

    # 3. 创建从起始月第一天到结束月最后一天的完整每日时间序列
    start_date = pd.to_datetime(list(ret.keys())[0] + "01", format="%Y%m%d")
    end_date = df_monthly.index[-1]
    daily_index = pd.date_range(start=start_date, end=end_date, freq="D")

    # 4. 将月度数据重采样到每日序列中，并进行线性插值
    df_daily = pd.DataFrame(index=daily_index)
    df_daily = df_daily.join(df_monthly["Value"])

    # 使用线性插值填满每天的空白（limit_direction='both' 可以向前后扩展未覆盖的几天）
    df_daily["Value"] = df_daily["Value"].interpolate(
        method="linear", limit_direction="both"
    )

    # 如果需要转回 Python 字典（键为 'YYYY-MM-DD' 字符串，值为插值）
    ret_daily_dict = (
        df_daily["Value"].round(6).set_axis(df_daily.index.strftime("%Y%m%d")).to_dict()
    )
    # print(ret_daily_dict)

    # # # 在图形中，对比插值前后
    # # # 在图形中，对比插值前后
    # x_time = [datetime.strptime(date, "%Y%m%d") for date in ret_daily_dict.keys()]
    # plt.plot(x_time, ret_daily_dict.values(), zorder=2)
    # x_time = [datetime.strptime(date, "%Y%m") for date in ret.keys()]
    # plt.plot(x_time, ret.values(), zorder=3)
    # plt.show()

    return ret_daily_dict
