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
import no_git

plt.rcParams["font.sans-serif"] = ["SimHei"]  # Windows/Linux 推荐
plt.rcParams["axes.unicode_minus"] = False


plt.figure(figsize=(10, 5))


# code = "002739.SZ"
code = "603711.SH"
# code = no_git.no_code[6]
date = 19900201
window_size = 1000000


# 获取单个股票数据
_, df = gp.gp.read_one(
    code, date, gp.tz.tz.__init_等地位_货币通胀(), gp.tz.tz.__init_等购买力_货币通胀()
)
最后交易日 = str(df.index[-1])  # 获取最后交易日
# df = df[df.index <= 20250228]
df.index = pd.to_datetime(df.index, format="%Y%m%d")  # 索引转日期


# 等地位数据
plt.plot(
    df["tz_等购买力"],
    color="blue",
    label=f"tz_等购买力 -> {df['tz_等购买力'].mean():.2f}",
)
plt.axhline(
    y=df["tz_等购买力"].mean(),
    color="blue",
    ls="--",
    alpha=0.6,
    # label=f"tz_等购买力 AVG: {gml_avg:.2f}",
)

# 等购买力 动态均线
多少交易日 = 100000
df["滚动均线_买"] = df["tz_等购买力"].rolling(window=多少交易日, min_periods=1).mean()
df["滚动均线_买"] /= 3
plt.plot(df["滚动均线_买"], label=f"滚动均线_买 -> {多少交易日}")

多少交易日 = 250
df["滚动均线_卖"] = df["tz_等购买力"].rolling(window=多少交易日, min_periods=1).mean()
df["滚动均线_卖"] *= 2.4
plt.plot(df["滚动均线_卖"], label=f"滚动均线_卖 -> {多少交易日}")

# 后复权力数据
plt.plot(df["hfq"], color="red", label=f"后复权 -> {df['hfq'].mean():.2f}")
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


# 等地位数据
plt.plot(df["tz_等地位"], color="g", label=f"tz_等地位 -> {df['tz_等地位'].mean():.2f}")
plt.axhline(
    y=df["tz_等地位"].mean(),
    color="g",
    ls="--",
    alpha=0.6,
    # label=f"tz_等地位 AVG: {ddw_avg:.2f}",
)


# 获取每日指标
每日指标 = gp.pub.pro.daily_basic(
    # trade_date=datetime.now().strftime("%Y%m%d"),
    trade_date=最后交易日,
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
    f"换手活跃度：{每日指标.volume_ratio}  "
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

plt.title(info)


# print("=========================================")
# print(t)
# print("=========================================")


# 滚动寻找信号
# 滚动平均值和最小值
rolling_min = df["tz_等购买力"].rolling(window=window_size, min_periods=1).min()
rolling_mean = df["tz_等购买力"].rolling(window=window_size, min_periods=1).mean()
滚动_mean = df["tz_等购买力"].rolling(window=250, min_periods=1).mean()
condition1 = df["tz_等购买力"] <= (rolling_min * 1.05)  # 滚动 是否最小值
condition2 = (rolling_min * 3) <= rolling_mean  # 是否小于历史平均值
# condition3 = (rolling_min * 1.5) < 滚动_mean  # 是否小于250天平均值
df["is_target"] = condition1 & condition2  # & condition3  # 添加标记

highlight_dates = df.index[df["is_target"]]
highlight_values = df.loc[df["is_target"], "tz_等购买力"]

highlight_scatter = plt.scatter(
    highlight_dates,
    highlight_values,
    color="y",  # 显眼的信号颜色
    s=30,  # 点的大小
    label="满足选股条件信号",
    zorder=3,  # 确保在折线上方
)

# ==================== 新增：标记大于平均2倍的点 ====================
# 这里的“平均”我用的是你定义的 90天滚动均线_2（你可以根据需求换成其他均线）
多少交易日 = 250
df["滚动均线_2"] = df["tz_等购买力"].rolling(window=多少交易日, min_periods=1).mean()

# 定义新条件：当前值 > 2 * 90天滚动均线
df["is_high_signal"] = df["tz_等购买力"] > (df["滚动均线_2"] * 2.4)

# 筛选新信号的数据
high_dates = df.index[df["is_high_signal"]]
high_values = df.loc[df["is_high_signal"], "tz_等购买力"]

print(high_values)

# 第二次调用 plt.scatter，使用不同的颜色（红色）和标记样式（X或大圆点）
high_scatter = plt.scatter(
    high_dates,
    high_values,
    color="g",  # 红色表示高位风险或突破
    marker="x",  # 使用 'x' 形状区分，也可以不加，单纯用颜色区分
    s=30,  # 让它稍微大一点
    label="大于均值2倍信号",
    zorder=4,  # 层级再高一层，避免被黄色点或折线覆盖
)

# ==================== 绘制折线和图例 ====================
plt.plot(df["滚动均线_2"], label=f"滚动均线_2 -> {多少交易日}")

# 记得调用 plt.legend()，这样两组 scatter 的 label 才会显示在图例里
plt.legend(loc="best")
# # # 4. 定义更新函数（滑块每次拖动都会自动调用它）


# def update(val):
# pass

# # 创建滑块
# slider_ax = plt.axes([0.2, 0.1, 0.6, 0.03])  # 滑块位置 [左, 下, 宽, 高]
# slope_slider = Slider(slider_ax, "斜率", valmin=0.1, valmax=10.0, valinit=2.0)
# slope_slider.on_changed(update)  # 绑定事件


plt.legend()
plt.grid(True)
plt.show()
