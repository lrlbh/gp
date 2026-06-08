import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import gp.gdp
import gp.m2
import gp.gp
from datetime import datetime

# gp.gp.更新()

开始时间 = "1991"


def 后复权数据(code):
    df = gp.gp.get_单个股票数据(code)

    # 冗余排顺
    df = df.sort_values(by="trade_date", ascending=True)

    首日数据 = df.iloc[0]
    上市发行价 = 首日数据.pre_close

    百分比 = 1
    后复权数据 = {}
    今日价格 = 上市发行价
    上一日_收盘价 = 上市发行价
    for data in df.itertuples():
        if data.pre_close != 上一日_收盘价:
            百分比 *= 上一日_收盘价 / data.pre_close
            # print(f"{data.trade_date} {百分比} 百分比")
        今日价格 += data.change * 百分比

        后复权数据[str(data.trade_date)] = 今日价格

        上一日_收盘价 = data.close

    return 后复权数据


gdp = gp.gdp.get_gdp_补偿(开始时间)
m2 = gp.m2.get_m2_补偿(开始时间)
货币贬值 = {key: m2[key] - gdp[key] for key in m2}
print(dict(list(货币贬值.items())[:10]))

x_time = [datetime.strptime(date, "%Y%m%d") for date in 货币贬值.keys()]
plt.plot(x_time, 货币贬值.values())

x_time = [datetime.strptime(date, "%Y%m%d") for date in gdp.keys()]
plt.plot(x_time, gdp.values())

x_time = [datetime.strptime(date, "%Y%m%d") for date in m2.keys()]
plt.plot(x_time, m2.values())

plt.show()


# print(f"this: {t[-1]:.2f}")
# print(f"len: {len(t)}")
# t = np.array(t)
# print(f"min: {min(t):.2f}")
# print(f"max: {max(t):.2f}")

hfq = 后复权数据("000001.sz")
x_time = [datetime.strptime(date, "%Y%m%d") for date in hfq.keys()]
plt.plot(x_time, hfq.values())


for key in hfq:
    # 最开始
    hfq[key] /= 1 + 货币贬值[key]

    # hfq[key] += hfq[key] * 货币贬值[key]


x_time = [datetime.strptime(date, "%Y%m%d") for date in hfq.keys()]
plt.plot(x_time, hfq.values())

plt.show()
