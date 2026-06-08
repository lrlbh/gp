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





gdp = gp.gdp.get_gdp_补偿("2000")
m2 = gp.m2.get_m2_补偿("2000")
print(m2)

x_time = [datetime.strptime(date, "%Y%m%d") for date in gdp.keys()]
plt.plot(x_time,gdp.values())

x_time = [datetime.strptime(date, "%Y%m%d") for date in m2.keys()]
plt.plot(x_time,m2.values())

plt.show()
# gm = {}
# for key in get_gdp_补偿: