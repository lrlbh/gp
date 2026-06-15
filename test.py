import time
import os
import gp.gp
import pandas as pd

开始时间 = "1990101"
start = ["TS", "T", "300", "688"]
end = ["BJ"]
status = ["D", "P", "G"]


codes = gp.gp.get_股票列表(False)
code_list = []
for row in codes.itertuples():
    code = row.ts_code

    # 部分股票没有数据，跳过
    # 部分股票代码,被回收复用,TS开头
    if code.startswith(tuple(start)):
        continue

    if code.endswith(tuple(end)):
        continue

    if row.list_status in status:
        continue

    code_list.append(code)
    # # 获取后复权股票数据

code = code_list[0]
文件路径 = os.path.join(gp.pub.单个股票path, f"{code}.csv")

# 测试1：纯读取到内存（不解析）
t0 = time.time()
with open(文件路径, "rb") as f:
    raw = f.read()
t1 = time.time()
print(f"纯读取: {(t1 - t0) * 1000:.2f}ms, 大小: {len(raw) / 1024:.1f}KB")

# 测试2：pandas解析
t0 = time.time()
df = pd.read_csv(文件路径, encoding="utf_8_sig", engine="pyarrow")
t1 = time.time()
print(f"pandas解析: {(t1 - t0) * 1000:.2f}ms")

# 测试3：单线程遍历所有文件（纯读取）
t0 = time.time()
for code in code_list:
    with open(os.path.join(gp.pub.单个股票path, f"{code}.csv"), "rb") as f:
        f.read()
t1 = time.time()
print(f"全部纯读取: {t1 - t0:.2f}s")
