import os.path
import time

import os
from pathlib import Path

import baostock as bs
import pandas as pd
import tl
import tl.dir
import atexit
import tushare as ts
from pathlib import Path
from datetime import datetime

# 保存数据的路径
data_path = os.path.join(Path(__file__).resolve().parent, "data")
# 股票列表的路径
股票列表path = os.path.join(data_path, "股票列表.csv")
# 单个股票数据的文件夹路径
单个股票path = os.path.join(data_path, "单个股票")

# Tushare Pro 的 token
ts_token = "7d6491af2d48adca24c66e8ab50f30e90559fb9741e1508dff218f17"

# 初始化 Tushare Pro 的 API
pro = ts.pro_api(ts_token)


# 创建 Baostock 连接管理器，确保登录状态和退出时的清理
def create_baostock_manager():
    is_logged_in = False

    def login():
        nonlocal is_logged_in
        if is_logged_in:
            return

        lg = bs.login()
        if lg.error_code == "0":
            is_logged_in = True
        else:
            raise ValueError(f"登录失败: {lg.error_msg}")

    def logout():
        nonlocal is_logged_in
        if is_logged_in:
            bs.logout()
            is_logged_in = False
            print("Baostock 连接已断开，状态已重置。")

    return login, logout


# 创建登录和退出函数
login, logout = create_baostock_manager()
# 结束时自动退出 Baostock 连接
atexit.register(logout)


def 股票代码转换(code):
    """
    将 Baostock 的股票代码转换为 Tushare Pro 的格式。
    Baostock 格式: sz.000001
    Tushare Pro 格式: 000001.SZ
    """
    if "." not in code:
        raise ValueError(f"无效的股票代码格式: {code}")

    # 转大写
    code_upper = code.upper()

    # 如果已经是 Tushare Pro 格式，直接返回
    if code_upper.endswith((".SZ", ".SH", ".BJ")):
        return code_upper

    # 否则按 Baostock 格式转换
    prefix, num = code_upper.split(".")
    if prefix == "SZ":
        return f"{num}.SZ"
    elif prefix == "SH":
        return f"{num}.SH"
    elif prefix == "BJ":
        return f"{num}.BJ"
    else:
        raise ValueError(f"未知的股票代码前缀: {prefix}")


# sz.000001,平安银行,1991-04-03,,1,1
def get_股票列表(更新=False, 更新间隔S=60 * 60):
    """
    code (证券代码) --> sz.000001
    code_name (证券名称) --> 平安银行 OR *ST国华
    ipoDate (上市日期) --> 1991-04-03
    outDate (退市日期) --> 2020-12-31 OR NaN
    type (证券类型) --> 1:股票 2:指数 3:其他
    status (上市状态) --> 1:在市 0:退市
    """

    # 文件存在、需要更新、且未超时，则直接加载
    # 文件存在
    if os.path.exists(股票列表path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(股票列表path).stat().st_mtime
        ).timestamp()

        # 是否需要更新
        if 更新 and time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(股票列表path, encoding="utf_8_sig")
            df["code"] = df["code"].apply(lambda x: 股票代码转换(x))
            return df

    # 更新数据
    print(f"更新股票列表 -> {股票列表path}")
    login()

    # 获取完整股票列表
    rs = bs.query_stock_basic()
    data_list = []
    while (rs.error_code == "0") & rs.next():
        data_list.append(rs.get_row_data())

    # 格式化数据为 DataFrame
    df = pd.DataFrame(data_list, columns=rs.fields)
    df["code"] = df["code"].apply(lambda x: 股票代码转换(x))

    # 确保文件夹存在
    tl.dir.ensure_path_exists(股票列表path)
    df.to_csv(股票列表path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    print(f"数据已成功保存至: {股票列表path}")

    return df


def 更新():
    退市列表 = []
    更新字典 = {}

    code_list = get_股票列表(True)
    code_list = code_list[code_list["type"] == 1]  # 筛选股票
    data_list = []

    # 通过强制拉去平安银行数据，判断交易日和最新交易日期
    交易日 = (
        get_单个股票数据(code="000001.SZ", 强制更新=True)["trade_date"]
        .astype(str)
        .tolist()
    )

    for row in code_list.itertuples():
        code = row.code

        # 部分股票没有数据，跳过
        if code in ["600849.SH"]:
            continue

        # 加载股票
        try:
            data_list.append(get_单个股票数据(code))
        except Exception as e:
            if (
                str(e)
                == "抱歉，您访问接口(daily)频率超限(50次/分钟)，具体频次详情：https://tushare.pro/document/1?doc_id=108。"
            ):
                print("请求过快，等待10秒...")
                time.sleep(10)
            else:
                raise e

        if row.status == 0:  # 退市
            退市列表.append(code)
            continue
        
        if data_list[-1]["trade_date"].values[-1]

        最后日期 = str(data_list[-1]["trade_date"].values[-1])
        if 最后日期 != 交易日[-1]:
            for item in 交易日:
                if item < 最后日期:
                    continue

                if item not in 更新字典:
                    更新字典[item] = []

                更新字典[item].append(code)

    print(f"退市数量: {len(退市列表)}")
    print(f"需要更新天数: {len(更新字典)}")
    for key in 更新字典:
        print(f"{key}: {更新字典[key]}")


def get_单个股票数据(code, start_date="19800101", end_date="33330101", 强制更新=False):
    """
    ts_code	str	股票代码
    trade_date	str	交易日期
    open	float	开盘价
    high	float	最高价
    low	float	最低价
    close	float	收盘价
    pre_close	float	昨收价【除权价】
    change	float	涨跌额
    pct_chg	float	涨跌幅(%) 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
    vol	float	成交量 （手）
    amount	float	成交额 （千元）
    """

    # 生成文件名
    单个股票文件 = os.path.join(单个股票path, f"{code}.csv")

    # 获取数据
    if os.path.exists(单个股票文件) and not 强制更新:
        df = pd.read_csv(单个股票文件, encoding="utf_8_sig")
        return df

    all_data = []
    offset = 0
    limit = 6000  # 每次最大6000条
    while True:
        # 拉取数据
        df = pro.daily(
            **{
                "ts_code": code,
                "trade_date": "",  # 获取指定某天的数据，忽略
                "start_date": start_date,
                "end_date": end_date,
                "limit": 6000,
                "offset": offset,
            },
            fields=[
                "ts_code",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "pre_close",
                "change",
                "pct_chg",
                "vol",
                "amount",
            ],
        )

        if df is None:
            raise Exception(f"返回df数据为None: {单个股票文件}")

        # 返回数据为空，退出循环
        if df.empty:
            break

        # 追加数据
        all_data.append(df)

        # 不足6000条，说明已经取完，退出循环
        if len(df) < limit:
            break

        offset += limit

    if all_data:
        tl.dir.ensure_path_exists(单个股票文件)
        df = pd.concat(all_data, ignore_index=True)
        if "trade_date" in df.columns:  # 排序
            df = df.sort_values(by="trade_date", ascending=True).reset_index(drop=True)
        df.to_csv(单个股票文件, index=False, encoding="utf_8_sig")
        print(f"数据已成功保存至: {单个股票文件}")
        return df

    raise Exception(f"空数据: {单个股票文件}")


if __name__ == "__main__":
    df = get_股票列表()

    # 筛选股票
    df = df[df["type"] == 1]
    print(f"股票数量: {len(df)} 只")

    # 筛选code的开头
    t = df[df["code"].str.startswith("sh.60")]
    print(f"code的开头 sh.60: {len(t)} 只")

    # 筛选code_name包含"*ST"的行, regex=False表示不使用正则表达式
    t = df[df["code_name"].str.contains("*ST", regex=False)]
    print(f"code_name包含 *ST: {len(t)} 只")

    # 筛选上市日期在2020年1月1日及以后的股票
    t = df[df["ipoDate"] >= "2020-01-01"]
    print(f"2020年1月1日及以后上市的股票数量: {len(t)} 只")

    # 将ipoDate列转换为日期类型
    df["ipoDate"] = pd.to_datetime(df["ipoDate"])

    # 按照上市日期排序
    df = df.sort_values(by="ipoDate")

    # 统计每个市场的股票数量
    t = df["code"].str[:2].value_counts()
    print(f"股票数量按市场分类:{t.to_dict()}")

    # 打印每列的数据类型
    # for col in df.columns:
    #     print(f"{col}: {df[col].dtype}")

    print(df.head())

    df = get_单个股票数据("sh.689009")
    print(df.head())
