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

# tz2.index = pd.to_datetime(tz2.index, format="%Y%m%d")
# plt.plot(tz2["temp_定基"], color="red", label="后复权", linestyle="--")
plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False
# gp.gp.更新()
# 1 / 0

date = 19900201
# date = 20240101


# 获取完整股票数据
df_list = gp.gp.get_all_股票数据(date)
最后交易日 = str(df_list["000001.SZ"].index[-1])
# 数据截止到某一天
# for key in df_list:
#     df_list[key] = df_list[key][df_list[key].index <= 20260617]

# 获取公司信息
公司信息 = gp.gp.get_股票列表(False)


# 获取每日指标
每日指标 = gp.pub.pro.daily_basic(
    # trade_date=datetime.now().strftime("%Y%m%d"),
    trade_date=最后交易日,
    fields=[],
)
追踪几个 = 10
exclude_starts = ("TS", "T", "300", "688", "301", "900", "200")  # 不要的开头
exclude_ends = ("BJ",)  # 不要结尾
条件_开头不含 = ~每日指标["ts_code"].str.startswith(exclude_starts)
条件_结尾不含 = ~每日指标["ts_code"].str.endswith(exclude_ends)
# 条件_pe有效 = 每日指标["pe_ttm"] > 0
# 条件_pb有效 = 每日指标["pe"] > 0
每日指标 = 每日指标[条件_开头不含 & 条件_结尾不含]  # & 条件_pe有效 & 条件_pb有效]
每日指标["ebs"] = (每日指标["pe"] + 每日指标["pb"] + 每日指标["ps"]) / 3
每日指标["ebs_ttm"] = (
    每日指标["pe"]
    + 每日指标["pe_ttm"]
    + 每日指标["pb"]
    + 每日指标["ps"]
    + 每日指标["ps_ttm"]
) / 5
每日指标["bs"] = (每日指标["pb"] + 每日指标["ps"]) / 2
每日指标["bs_ttm"] = (每日指标["pb"] + 每日指标["ps"] + 每日指标["ps_ttm"]) / 3

ebs = 每日指标.sort_values(by="ebs", ascending=True).head(追踪几个)["ts_code"].tolist()

ebs_ttm = (
    每日指标.sort_values(by="ebs_ttm", ascending=True)
    .head(追踪几个)["ts_code"]
    .tolist()
)
bs = 每日指标.sort_values(by="bs", ascending=True).head(追踪几个)["ts_code"].tolist()
bs_ttm = (
    每日指标.sort_values(by="bs_ttm", ascending=True).head(追踪几个)["ts_code"].tolist()
)
pb = 每日指标.sort_values(by="pb", ascending=True).head(追踪几个)["ts_code"].tolist()
ps = 每日指标.sort_values(by="ps", ascending=True).head(追踪几个)["ts_code"].tolist()
ps_ttm = (
    每日指标.sort_values(by="ps_ttm", ascending=True).head(追踪几个)["ts_code"].tolist()
)
pe = 每日指标.sort_values(by="pe", ascending=True).head(追踪几个)["ts_code"].tolist()
pe_ttm = (
    每日指标.sort_values(by="pe_ttm", ascending=True).head(追踪几个)["ts_code"].tolist()
)

dv = (
    每日指标.sort_values(by="dv_ratio", ascending=False)
    .head(追踪几个)["ts_code"]
    .tolist()
)
dv_ttm = (
    每日指标.sort_values(by="dv_ttm", ascending=False)
    .head(追踪几个)["ts_code"]
    .tolist()
)


file_name = "test/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

已收录 = []


def test(
    df_list,
    列名,
    重复收录=False,
    追踪code=[],
    忽略code=[],
    忽略均值=2.7,
    低价阈值=1.05,
    提示头部文字="",
):
    低于史地多少 = 0.03

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
        if (
            this < t_min * 低价阈值
            and t_avg / t_min >= 忽略均值
            and code not in 忽略code
        )
        or code in 追踪code
    }

    # 打开文件
    f = open(
        file_name,
        "a",
        encoding="utf-8",
    )

    # 写入基础信息
    if 提示头部文字 != "":
        f.write(提示头部文字 + "\n")
    f.write(
        f"{列名},史低股数量: {len(df_筛选后)}\t起点日期: {date}\t史地阈值: {低价阈值} 平均值阈值: {忽略均值}\t重复收录: {重复收录}\n"
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
                f"穿低{低于史地多少 * 100:.0f}%",
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
        if not 重复收录:
            if key in 已收录:
                continue
            else:
                已收录.append(key)

        this_每日指标 = 每日指标.loc[每日指标["ts_code"] == key].iloc[0]
        this_公司信息 = 公司信息.loc[公司信息["ts_code"] == key].iloc[0]

        df = df_筛选后[key]
        最低价 = df[列名].min()
        平均价 = df[列名].mean()
        当前价 = df[列名].iloc[-1]
        上市时间 = df.index[0]
        公司名 = this_公司信息["name"]
        公司名 = 公司名 + "  " if len(公司名) <= 3 else 公司名
        股票代码 = key
        实际价格 = df["close"].iloc[-1]
        历史平均值倍率 = 平均价 / 最低价
        高于史地多少 = 当前价 / 最低价
        多少价格史地 = 实际价格 / 高于史地多少

        低于史地 = 多少价格史地 - (多少价格史地 * 低于史地多少)
        # 价格修正 = 历史平均值倍率 / 3
        # if 历史平均值倍率 < 3:
        #     购入金额 = 3000 * 价格修正 * 价格修正
        # elif 历史平均值倍率 > 4:
        #     购入金额 = 3000 * 1.33
        # else:
        #     购入金额 = 3000 * 价格修正

        提示信息 = ""
        if 股票代码 in no_git.msg:
            提示信息 = "\n\t" + no_git.msg[股票代码]

        t_str = (
            f"{公司名}\t"
            + f"{股票代码}\t"
            + f"{上市时间}\t"
            # + f"{t_this:.2f}\t"
            # + f"{t_min:.2f}\t"
            # + f"{avg:.2f}\t"
            + f"{实际价格:.2f}\t"
            + f"{多少价格史地:.3f}\t"
            + f"{高于史地多少:.3f}\t"
            + f"{低于史地:.3f}\t"
            + f"{历史平均值倍率:.2f}"
            # + f"{购入金额:.0f}"
            + f"\n\t实控人: {this_公司信息.act_name}-->{this_公司信息.act_ent_type}\t"
            + f"地域: {this_公司信息.area}\t"
            + f"行业: {this_公司信息.industry}\t"
            # + f"股息: {this_每日指标.dv_ratio:.2f}%-->{this_每日指标.dv_ttm:.2f}%"
            + f"\n\t总值: {this_每日指标.total_mv / 10000:.2f}\t"
            + f"流值: {this_每日指标.circ_mv / 10000:.2f}\t"
            + f"市净b: {this_每日指标.pb:.2f}\t"
            + f"市销s: {this_每日指标.ps:.2f}-->{this_每日指标.ps_ttm:.2f}\t"
            + f"市盈e: {this_每日指标.pe:.2f}-->{this_每日指标.pe_ttm:.2f}\t"
            + f"\n\tebs:{this_每日指标.ebs:.2f}\t"
            + f"\tebs_ttm:{this_每日指标.ebs_ttm:.2f}\t"
            + f"\tbs:{this_每日指标.bs:.2f}\t"
            + f"\tbs_ttm:{this_每日指标.bs_ttm:.2f}\t"
            + f"{提示信息}"
            + "\n\n"
        )

        f.write(t_str)

    f.write("\n\n\n\n\n\n")
    f.close()


def test_2(
    df_list,
    列名,
    追踪code=[],
    忽略code=[],
    提示头部文字="",
):
    # 打开文件
    f = open(
        file_name,
        "a",
        encoding="utf-8",
    )

    # 写入基础信息
    if 提示头部文字 != "":
        f.write(提示头部文字 + "\n")

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
            ]
        )
        + "\n"
    )

    for key in 追踪code:
        this_每日指标 = 每日指标.loc[每日指标["ts_code"] == key].iloc[0]
        this_公司信息 = 公司信息.loc[公司信息["ts_code"] == key].iloc[0]
        # if this_公司信息.industry in ["建筑工程", "银行"]:
        #     continue

        if key not in df_list:
            continue
        df = df_list[key]
        最低价 = df[列名].min()
        当前价 = df[列名].iloc[-1]
        上市时间 = df.index[0]
        公司名 = this_公司信息["name"]
        公司名 = 公司名 + "  " if len(公司名) <= 3 else 公司名
        股票代码 = key
        实际价格 = df["close"].iloc[-1]
        高于史地多少 = 当前价 / 最低价
        多少价格史地 = 实际价格 / 高于史地多少

        提示信息 = ""
        if 股票代码 in no_git.msg:
            提示信息 = "\n\t" + no_git.msg[股票代码]

        t_str = (
            f"{公司名}\t"
            + f"{股票代码}\t"
            + f"{上市时间}\t"
            # + f"{t_this:.2f}\t"
            # + f"{t_min:.2f}\t"
            # + f"{avg:.2f}\t"
            + f"{实际价格:.2f}\t"
            + f"{多少价格史地:.3f}\t"
            + f"{高于史地多少:.2f}\t"
            # + f"{购入金额:.0f}"
            + f"\n\t实控人: {this_公司信息.act_name}-->{this_公司信息.act_ent_type}\t"
            + f"地域: {this_公司信息.area}\t"
            + f"行业: {this_公司信息.industry}\t"
            + f"股息: {this_每日指标.dv_ratio:.2f}%-->{this_每日指标.dv_ttm:.2f}%"
            + f"\n\t总值: {this_每日指标.total_mv / 10000:.2f}\t"
            + f"流值: {this_每日指标.circ_mv / 10000:.2f}\t"
            + f"市净b: {this_每日指标.pb:.2f}\t"
            + f"市销s: {this_每日指标.ps:.2f}-->{this_每日指标.ps_ttm:.2f}\t"
            + f"市盈e: {this_每日指标.pe:.2f}-->{this_每日指标.pe_ttm:.2f}\t"
            + f"\n\tebs:{this_每日指标.ebs:.2f}\t"
            + f"\tebs_ttm:{this_每日指标.ebs_ttm:.2f}\t"
            + f"\tbs:{this_每日指标.bs:.2f}\t"
            + f"\tbs_ttm:{this_每日指标.bs_ttm:.2f}\t"
            + f"{提示信息}"
            + "\n\n"
        )

        f.write(t_str)

    f.write("\n\n\n\n\n\n")
    f.close()


# 史地股票
test(df_list, "tz_等购买力", 低价阈值=1.01, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.015, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.02, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.03, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.05, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.10, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.15, 忽略均值=1.5, 忽略code=no_git.no_code)
test(df_list, "tz_等购买力", 低价阈值=1.20, 忽略均值=1, 忽略code=no_git.no_code)

# 显示指定股票
test_2(
    df_list,
    "tz_等购买力",
    追踪code=no_git.追踪code,
    提示头部文字="手动追踪的股票",
)


# PE PB PS 股票
test_2(
    df_list,
    "tz_等购买力",
    追踪code=ebs,
    提示头部文字="PE PB PS 综合头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=ebs_ttm,
    提示头部文字="PE PB PS 加上ttm权重的综合头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=bs,
    提示头部文字="PB PS 综合头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=bs_ttm,
    提示头部文字="PB PS 加上ttm权重的综合头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=pb,
    提示头部文字="pb 头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=ps,
    提示头部文字="ps 头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=ps_ttm,
    提示头部文字="ps_ttm 头部",
)
test_2(
    df_list,
    "tz_等购买力",
    追踪code=pe,
    提示头部文字="pe 头部",
)

test_2(
    df_list,
    "tz_等购买力",
    追踪code=pe_ttm,
    提示头部文字="pe_ttm 头部",
)

test_2(
    df_list,
    "tz_等购买力",
    追踪code=dv,
    提示头部文字="股息 头部",
)

test_2(
    df_list,
    "tz_等购买力",
    追踪code=dv_ttm,
    提示头部文字="股息_ttm 头部",
)

# 史地股票,hfq
# test(df_list, "hfq", 低价阈值=1.20, 重复收录=True, 忽略均值=1, 忽略code=no_git.no_code)
