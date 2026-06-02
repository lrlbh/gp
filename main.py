
import matplotlib.pyplot as plt
import pandas as pd
import time
import tushare as ts
import numpy as np
import akshare as ak
import gp


# 拉取数据
df = gp.pro.cn_gdp(**{
    "q": "",
    "start_q": "1990Q",
    "end_q": "",
    "limit": "",
    "offset": ""
}, fields=[
    "quarter",
    "gdp",
    "gdp_yoy",
    "pi",
    "pi_yoy",
    "si",
    "si_yoy",
    "ti",
    "ti_yoy"
])
print(df)



# 拉取数据
df = gp.pro.cn_m(**{
    "m": "",
    "start_m": "19900101",
    "end_m": "",
    "limit": "",
    "offset": ""
}, fields=[
    "month",
    "m0",
    "m0_yoy",
    "m0_mom",
    "m1",
    "m1_yoy",
    "m1_mom",
    "m2",
    "m2_yoy",
    "m2_mom"
])
print(df)

        


1/0

gp.更新()





