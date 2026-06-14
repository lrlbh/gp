import os
import tushare as ts
from pathlib import Path

data_path = os.path.join(
    Path(__file__).resolve().parent.parent, "data"
)  # 保存数据的路径
单个股票path = os.path.join(data_path, "单个股票")  # 单个股票数据的文件夹路径
股票列表path = os.path.join(data_path, "股票列表.csv")  # 股票列表的路径
gdp_path = os.path.join(data_path, "gdp.csv")
m2_path = os.path.join(data_path, "m2.csv")
人口_path = os.path.join(data_path, "人口.csv")

# Tushare Pro 的 token
ts_token = "0e29e046df7990e93a881879bf0970f61aaa7cdaade91c97f4d6d412"
# 初始化 Tushare Pro 的 API
pro = ts.pro_api(ts_token)
