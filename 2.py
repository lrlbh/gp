from cProfile import label

import matplotlib.pyplot as plt
import pandas as pd

import gp.pub


code = [
    "601398.SH",  # 工商银行
    "001227.SZ",  # 兰州银行
    "601997.SH",  # 贵阳银行
    "001227.SZ",  # 兰州银行
    "601860.SH",  # 紫金银行
    "600928.SH",  # 西安银行
    "002958.SZ",  # 青农商行
    "002839.SZ",  # 张家港行
    "601997.SH",  # 贵阳银行
    "600908.SH",  # 无锡银行
    "601528.SH",  # 瑞丰银行
    "601916.SH",  # 浙商银行
    "600015.SH",  # 华夏银行
    "600016.SH",  # 民生银行
    "603323.SH",  # 苏农银行
    "601577.SH",  # 长沙银行
    ""
]

# 获取每日指标
每日指标 = gp.pub.pro.daily_basic(
    # trade_date=datetime.now().strftime("%Y%m%d"),
    # ts_code="600660.SH",
    ts_code="600309.SH",
    # fields=[],
)
每日指标["trade_date"] = pd.to_datetime(每日指标["trade_date"], format="%Y%m%d")
每日指标.set_index("trade_date", inplace=True)
每日指标.sort_index(inplace=False)

plt.plot(每日指标["pe"], label="pe")
plt.plot(每日指标["pe_ttm"], label="pe_ttm")
plt.plot(每日指标["pb"], label="pb")
plt.plot(每日指标["ps"], label="ps")
plt.plot(每日指标["ps_ttm"], label="ps_ttm")
# plt.plot(每日指标["total_mv"], label="总市值")

plt.legend()
plt.grid(True)

plt.show()
