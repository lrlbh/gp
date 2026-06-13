import os.path
import time
import os
from pathlib import Path
import pandas as pd
import tl
import tl.dir
from datetime import datetime
import gp.pub


def get_gdp(更新=False, 更新间隔S=60 * 60 * 24):
    # 是否需要更新
    if os.path.exists(gp.pub.gdp_path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(gp.pub.gdp_path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(gp.pub.gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(gp.pub.gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新GDP -> {gp.pub.gdp_path}")
    df = gp.pub.pro.cn_gdp(
        **{"q": "", "start_q": "", "end_q": "", "limit": "", "offset": ""},
        fields=[
            "quarter",
            "gdp",
            "gdp_yoy",
            "pi",
            "pi_yoy",
            "si",
            "si_yoy",
            "ti",
            "ti_yoy",
        ],
    )

    # 写入到文件
    tl.dir.ensure_path_exists(gp.pub.gdp_path)
    df.to_csv(gp.pub.gdp_path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {gdp_path}")
    if len(df) >= 5999:
        print("WAR: GDP数据可能溢出了")

    return df


def get_gdp_插值():
    """
    补齐GDP季度数据：
    1. 补齐早期（1952-1991）只有Q4的年份 -> Q1-Q3
    2. 外推未来年份到当前年（基于最近5年Q4平均增速）
    """

    df = get_gdp(True)

    current_year = datetime.now().year  # 2026

    # ========== 1. 创建完整季度索引（从数据最早年到当前年） ==========
    min_year = df["quarter"].str[:4].astype(int).min()
    years = range(min_year, current_year + 1)
    full_quarters = [f"{y}Q{q}" for y in years for q in range(1, 5)]

    df_full = pd.DataFrame({"quarter": full_quarters})
    df_full = df_full.merge(df, on="quarter", how="left")

    # ========== 2. 计算现代数据的平均季度比例（用于拆分累计值） ==========
    modern = df_full[df_full["quarter"].str[:4].astype(int) >= 1992].copy()

    ratios = {}
    for col in ["gdp", "pi", "si", "ti"]:
        modern["year"] = modern["quarter"].str[:4].astype(int)
        modern["q"] = modern["quarter"].str[-1].astype(int)
        pivot = modern.pivot(index="year", columns="q", values=col)
        ratios[col] = {
            1: (pivot[1] / pivot[4]).mean(),
            2: (pivot[2] / pivot[4]).mean(),
            3: (pivot[3] / pivot[4]).mean(),
            4: 1.0,
        }

    # ========== 3. 补齐早期只有Q4的年份（1952-1991） ==========
    early_years = range(1952, 1992)

    for _, row in df_full.iterrows():
        year = int(row["quarter"][:4])
        q = int(row["quarter"][-1])

        if year in early_years and q == 4 and pd.notna(row["gdp"]):
            # 拆分累计值
            for target_q in [1, 2, 3]:
                target = f"{year}Q{target_q}"
                idx = df_full[df_full["quarter"] == target].index[0]
                for col in ["gdp", "pi", "si", "ti"]:
                    df_full.loc[idx, col] = row[col] * ratios[col][target_q]
            # 补齐yoy（用Q4的yoy填充Q1-Q3）
            for target_q in [1, 2, 3]:
                target = f"{year}Q{target_q}"
                idx = df_full[df_full["quarter"] == target].index[0]
                for col in ["gdp_yoy", "pi_yoy", "si_yoy", "ti_yoy"]:
                    if pd.notna(row[col]):
                        df_full.loc[idx, col] = row[col]

    # ========== 4. 外推未来年份到当前年 ==========
    actual_years = df_full.dropna(subset=["gdp"])["quarter"].str[:4].astype(int)
    last_actual_year = actual_years.max()

    if last_actual_year < current_year:
        # 计算最近5年Q4的平均同比增长率
        recent_years = range(last_actual_year - 4, last_actual_year + 1)
        recent_q4 = df_full[
            (df_full["quarter"].str[:4].astype(int).isin(recent_years))
            & (df_full["quarter"].str[-1] == "4")
        ].sort_values("quarter")

        avg_yoy = {}
        for col in ["gdp", "pi", "si", "ti"]:
            yoy_col = col + "_yoy"
            valid_yoy = recent_q4[yoy_col].dropna()
            if len(valid_yoy) >= 2:
                avg_yoy[col] = valid_yoy.mean() / 100
            else:
                # 无yoy时，用实际值算复合增长率
                vals = recent_q4[col].dropna()
                if len(vals) >= 2:
                    avg_yoy[col] = (vals.iloc[-1] / vals.iloc[0]) ** (
                        1 / (len(vals) - 1)
                    ) - 1
                else:
                    avg_yoy[col] = 0.05  # 默认5%

        # 逐年后推
        for year in range(last_actual_year + 1, current_year + 1):
            prev_year_q4 = df_full[df_full["quarter"] == f"{year - 1}Q4"]
            if prev_year_q4.empty:
                continue

            for col in ["gdp", "pi", "si", "ti"]:
                prev_val = prev_year_q4[col].values[0]
                if pd.isna(prev_val):
                    continue

                pred_q4 = prev_val * (1 + avg_yoy[col])

                # 填充Q4
                q4_idx = df_full[df_full["quarter"] == f"{year}Q4"].index[0]
                df_full.loc[q4_idx, col] = pred_q4
                df_full.loc[q4_idx, col + "_yoy"] = avg_yoy[col] * 100

                # 用比例拆分Q1-Q3
                for q in [1, 2, 3]:
                    q_idx = df_full[df_full["quarter"] == f"{year}Q{q}"].index[0]
                    df_full.loc[q_idx, col] = pred_q4 * ratios[col][q]
                    df_full.loc[q_idx, col + "_yoy"] = avg_yoy[col] * 100

    return df_full.sort_values("quarter").reset_index(drop=True)


# 原始数据插值前后
# def show_gdp_插值():
#     df = gp.get_gdp()
#     # df = df[df["quarter"] < "2000"]
#     df["quarter"] = pd.to_datetime(df["quarter"]) + pd.offsets.QuarterEnd(0)
#     df = df.sort_values(by="quarter", ascending=True).reset_index(drop=True)

#     df_full = gp.get_gdp_插值()
#     # df_full = df_full[df_full["quarter"] < "2000"]
#     df_full["quarter"] = pd.to_datetime(df_full["quarter"]) + pd.offsets.QuarterEnd(0)
#     df_full = df_full.sort_values(by="quarter", ascending=True).reset_index(drop=True)

#     plt.plot(df["quarter"], df["gdp"], zorder=3)
#     plt.plot(df_full["quarter"], df_full["gdp"], zorder=2)

#     plt.show()
# show_gdp_插值()


def get_gdp_补偿(开始日期="1991"):

    # 返回值
    ret = {}

    # 获取gdp数据
    df = get_gdp_插值()

    # 前一年的 Q1~Q4 GDP数据
    季度基值 = {"Q1": None, "Q2": None, "Q3": None, "Q4": None}
    for key in 季度基值:
        季度基值[key] = df[df["quarter"] == str(int(开始日期) - 1) + key].gdp.item()

    # 对比前一年的，同比增长数据
    总年数 = int(datetime.now().strftime("%Y")) - int(开始日期) + 1
    for i in range(总年数):
        当前年 = str(int(开始日期) + i)
        for key in 季度基值:
            本季gdp = df.loc[df["quarter"] == 当前年 + key, "gdp"].values[0]
            本季gdp = (本季gdp - 季度基值[key]) / 季度基值[key]  # 增长百分比
            ret[当前年 + key] = 本季gdp
            # if key == "Q1":
            # print(f"{当前年 + key} {本季gdp}")

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

    # # 滤波
    # import statsmodels.api as sm
    # lamb = 1.6e11
    # cycle, trend = sm.tsa.filters.hpfilter(df_daily["ret_daily"], lamb=lamb)
    # df_daily["gdp_true_trend"] = trend  # 这就是你用来修正商品价格的真实倍数
    # # # 在图形中，对比插值前后
    # # # 在图形中，对比插值前后
    # df_daily["date"] = pd.to_datetime(df_daily["date"])
    # new_dict_end = {pd.Period(k, freq="Q").end_time: v for k, v in ret.items()}
    # plt.plot(df_daily["date"], df_daily["ret_daily"], zorder=2)
    # plt.plot(df_daily["date"], df_daily["gdp_true_trend"], zorder=2)
    # plt.plot(new_dict_end.keys(), new_dict_end.values(), zorder=3)
    # plt.show()

    ret_daily_dict = df_daily.set_index(df_daily["date"].dt.strftime("%Y%m%d"))[
        "ret_daily"
    ].to_dict()
    return ret_daily_dict
