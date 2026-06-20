import os

import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp.pub
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


plt.figure(figsize=(10, 5))

code = "002573.SZ"
date = 19900201

# # 市值接口
# all_data = []
# df = gp.pub.pro.daily_basic(
#     ts_code=code,
#     start_date="1990011",
#     end_date="20991231",
#     fields=[],
#     limit=6000,
#     offset=0,
# )
# all_data.append(df)
# df = gp.pub.pro.daily_basic(
#     ts_code=code,
#     start_date="1990011",
#     end_date="20991231",
#     fields=[],
#     limit=6000,
#     offset=6000,
# )
# all_data.append(df)
# df = pd.concat(all_data, ignore_index=True)

# df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
# df = df.set_index("trade_date").sort_index(ascending=True)

# plt.plot(df["total_mv"], color="red", label="后复权")
# plt.legend()
# plt.grid(True)
# plt.show()


# 获取单个股票数据
start = time.time()
_, df = gp.gp.read_one(
    code, date, gp.tz.tz.__init_等地位_货币通胀(), gp.tz.tz.__init_等购买力_货币通胀()
)
print(time.time() - start)

# 获取最后交易日
最后交易日 = str(df.index[-1])


# 索引转日期
df.index = pd.to_datetime(df.index, format="%Y%m%d")
# df = df.loc[:"2015-06-03"]


# df["3000"] = df["tz_等购买力"].rolling(window=300, min_periods=1).mean()
# df["1500"] = df["tz_等购买力"].rolling(window=150, min_periods=1).mean()


# 等地位数据
plt.plot(df["tz_等购买力"], color="blue", label="tz_等购买力")
plt.axhline(
    y=df["tz_等购买力"].mean(),
    color="blue",
    ls="--",
    alpha=0.6,
    # label=f"tz_等购买力 AVG: {gml_avg:.2f}",
)

# 等购买力数据
plt.plot(df["tz_等地位"], color="g", label="tz_等地位")
plt.axhline(
    y=df["tz_等地位"].mean(),
    color="g",
    ls="--",
    alpha=0.6,
    # label=f"tz_等地位 AVG: {ddw_avg:.2f}",
)


# 后复权力数据
plt.plot(df["hfq"], color="red", label="后复权")
plt.axhline(
    y=df["hfq"].mean(),
    color="red",
    ls="--",
    alpha=0.6,
    # label=f"后复权 AVG: {hfq_avg:.2f}",
)
# 最大值
idx = df["hfq"].idxmax()
val = df.loc[idx, "hfq"]
date_str = idx.strftime("%Y-%m-%d")  # 格式自行调整
plt.scatter(idx, val, color="red")
plt.text(idx, val, f"{val:.2f}\n{date_str}", ha="center", va="bottom")

# 最小值
idx = df["hfq"].idxmin()
val = df.loc[idx, "hfq"]
date_str = idx.strftime("%Y-%m-%d")
plt.scatter(idx, val, color="red")
plt.text(idx, val, f"{val:.2f}\n{date_str}", ha="center", va="bottom")

# 当前值（最后一条数据）
idx = df.index[-1]
val = df.loc[idx, "hfq"]
date_str = idx.strftime("%Y-%m-%d")
plt.scatter(idx, val, color="blue")
plt.text(idx, val, f"{val:.2f}\n{date_str}", ha="center", va="bottom")


# plt.plot(df["3000"], label="10")
# plt.plot(df["1500"], label="20")


# 获取每日指标
每日指标 = gp.pub.pro.daily_basic(
    # trade_date=datetime.now().strftime("%Y%m%d"),
    trade_date="20260618",
    fields=[],
)
每日指标 = 每日指标.loc[每日指标["ts_code"] == code].iloc[0]

# 获取股票曾用名
曾用名 = gp.pub.pro.namechange(ts_code=code)
曾用名 = 曾用名.drop_duplicates()  # 去重
曾用名 = 曾用名.drop_duplicates(subset=["start_date"])  # 去重
曾用名 = 曾用名.sort_values("start_date")
名称字符串 = " -> ".join(曾用名["name"])

# 获取公司信息
公司信息 = gp.pub.pro.stock_basic(ts_code=code)
公司信息 = 公司信息.iloc[0]

# 添加提示文本
info = (
    f"公司名称: {公司信息['name']}  "
    f"股票代码：{code}  "
    f"交易日期：{每日指标.trade_date}  "
    f"收盘价：{每日指标.close:.2f}\n"
    f"换手率：{每日指标.turnover_rate:.2f}%  "
    f"自由换手率：{每日指标.turnover_rate_f:.2f}%  "
    f"换手活跃度：{每日指标.volume_ratio:.2f}  "
    f"地域: {公司信息.area}  "
    f"行业: {公司信息.industry}  "
    f"实控人: {公司信息.act_name}  "
    f"实控人性质: {公司信息.act_ent_type}\n"
    f"市盈率：{每日指标.pe:.2f}  "
    f"市盈率(TTM)：{每日指标.pe_ttm:.2f}  "
    f"市净率：{每日指标.pb:.2f}  "
    f"市销率：{每日指标.ps:.2f}  "
    f"市销率(TTM)：{每日指标.ps_ttm:.2f}  "
    f"股息率：{每日指标.dv_ratio:.2f}%  "
    f"股息率(TTM)：{每日指标.dv_ttm:.2f}%\n"
    f"总股本：{每日指标.total_share:,.0f} 万股  "
    f"流通股本：{每日指标.float_share:,.0f} 万股  "
    f"实际流通股：{每日指标.free_share:,.0f} 万股  "
    f"总市值：{每日指标.total_mv / 10000:,.2f} 亿元  "
    f"流通市值：{每日指标.circ_mv / 10000:,.2f} 亿元\n"
    f"{名称字符串}"
)
# plt.text(
#     0.02,
#     0.98,
#     info,
#     transform=plt.gca().transAxes,
#     fontsize=11,
#     va="top",
#     bbox=dict(facecolor="white", alpha=0.8),
# )


plt.title(info)
plt.legend()
plt.grid(True)
plt.show()
