import os.path
import time
import os
from pathlib import Path
import pandas as pd
import gp.tz.tz
import tl
import tl.dir
from datetime import datetime
import gp.pub
import gp.tz.gdp
import gp.tz.m2
import numpy as np
from joblib import Parallel, delayed


def get_股票列表(更新=False, 更新间隔S=60):

    # 是否需要更新
    if os.path.exists(gp.pub.股票列表path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(gp.pub.股票列表path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(gp.pub.股票列表path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: 股票列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(gp.pub.股票列表path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: 股票列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新股票列表 -> {gp.pub.股票列表path}")
    df = gp.pub.pro.stock_basic(
        **{
            "ts_code": "",
            "name": "",
            "exchange": "",
            "market": "",
            "is_hs": "",
            "list_status": "L,D,P,G",
            "limit": "",
            "offset": "",
        },
        fields=[
            "ts_code",
            "symbol",
            "name",
            "area",
            "industry",
            "cnspell",
            "market",
            "list_date",
            "act_name",
            "act_ent_type",
            "delist_date",
            "is_hs",
            "list_status",
            "curr_type",
            "exchange",
            "enname",
            "fullname",
        ],
    )

    # 写入到文件
    tl.dir.ensure_path_exists(gp.pub.股票列表path)
    df.to_csv(
        gp.pub.股票列表path, index=False, encoding="utf_8_sig"
    )  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {股票列表path}")
    if len(df) >= 5999:
        print("WAR: 股票列表数据可能溢出了")

    return df


def 更新():
    退市列表 = []
    暂停上市列表 = []
    未交易列表 = []
    更新字典 = {}
    更新失败的股票 = {}

    code_list = get_股票列表(True)
    code_list = code_list[
        code_list["ts_code"].str.endswith(("SH", "SZ"))
    ]  # 筛选需要的股票
    data_list = []

    # 通过强制拉取平安银行数据，获取交易日和最新交易日期
    交易日 = (
        get_单个股票数据(code="000001.SZ", 强制更新=True, 不允许下载=False)[
            "trade_date"
        ]
        .astype(str)
        .tolist()
    )

    # 加载每只股票然后判断那些需要更新
    for row in code_list.itertuples():
        code = row.ts_code

        # 忽略非上市股票
        if row.list_status == "D":
            退市列表.append(code)
            continue
        if row.list_status == "P":
            暂停上市列表.append(code)
            continue
        if row.list_status == "G":
            未交易列表.append(code)
            continue

        # 部分股票没有数据，跳过
        # 部分股票代码,被回收复用,TS开头
        if code.startswith("TS"):
            continue

        # 加载股票
        try:
            data_list.append(get_单个股票数据(code, 不允许下载=False))
        except Exception as e:
            if "抱歉，您访问接口(daily)频率超限" in str(e):
                print("请求过快，等待1.5秒...")
                time.sleep(1.5)
            else:
                raise e

        # 统计需要更新股票
        最后日期 = str(data_list[-1]["trade_date"].values[-1])
        if 最后日期 != 交易日[-1]:
            for item in 交易日:
                if item <= 最后日期:
                    continue

                if item not in 更新字典:
                    更新字典[item] = []

                更新字典[item].append(code)

    for key in 更新字典:
        if len(更新字典[key]) >= 500:
            t_code = ""
        else:
            t_code = ",".join(更新字典[key])
        df = gp.pub.pro.daily(
            **{
                "ts_code": t_code,
                "trade_date": key,
                "start_date": "",
                "end_date": "",
                "limit": "",
                "offset": "",
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
        # print(df)
        for code in 更新字典[key]:
            code_data = df[df["ts_code"] == code]
            if code_data.empty:
                if code not in 更新失败的股票:
                    更新失败的股票[code] = []
                更新失败的股票[code].append(key)

            单个股票文件 = os.path.join(gp.pub.单个股票path, f"{code}.csv")
            code_data.to_csv(
                单个股票文件,
                mode="a",  # 'a' 表示追加写入 (Append)
                header=False,  # False 表示不要表头 (Columns)
                index=False,  # False 表示不要行编号 (Index)
                encoding="utf_8_sig",  # 防止中文乱码
            )

        # print(f"{key} {len(df)}")

    需要更新股票 = set()
    print(
        f"股票总数: {len(code_list)} 退市: {len(退市列表)} 暂停上市: {len(暂停上市列表)} 未交易: {len(未交易列表)}"
    )
    for key in 更新字典:
        需要更新股票.update(更新字典[key])
    #     print(f"{key}: {len(更新字典[key])}")
    print(f"需要更新天数: {len(更新字典)}")
    print(f"需要更新股票数量: {len(需要更新股票)} 失败数量: {len(更新失败的股票)} ")
    print(f"更新失败股票: {更新失败的股票.keys()}")


def get_单个股票数据(
    code, start_date="19800101", end_date="33330101", 强制更新=False, 不允许下载=True
):
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
    单个股票文件 = os.path.join(gp.pub.单个股票path, f"{code}.csv")

    # 获取数据
    if os.path.exists(单个股票文件) and not 强制更新:
        # 要读取的列 = ["trade_date", "close", "pre_close", "change"]
        df = pd.read_csv(
            单个股票文件,
            encoding="utf_8_sig",
            engine="pyarrow",
            # usecols=要读取的列,
            # dtype={"trade_date": str},
        )
        return df

    if 不允许下载:
        print(f"缺少股票: {code} 同时不允许下载")
        return None

    all_data = []
    offset = 0
    limit = 6000  # 每次最大6000条
    while True:
        # 拉取数据
        df = gp.pub.pro.daily(
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


def read_one(code, 开始时间, tz, tz2):
    try:
        df = get_单个股票数据(code, 不允许下载=True)

        if df.empty:
            print(f"空数据 {code}")
            return code, None

        # 添加后复权列
        last_close = df["close"].shift(1).fillna(df["pre_close"].iloc[0])
        daily_factor = np.where(
            df["pre_close"] != last_close, last_close / df["pre_close"], 1.0
        )
        cum_factor = daily_factor.cumprod()
        hfq_change = df["change"] * cum_factor
        df["hfq"] = df["pre_close"].iloc[0] + hfq_change.cumsum()

        # 筛选开始日期
        df = df[df["trade_date"] >= 开始时间]
        开始时间 = df["trade_date"].min()
        df.set_index("trade_date", inplace=True)

        # print(f"{开始时间}  {code}")

        # 通胀校准到当天
        基准值 = tz.loc[开始时间, "定基增长率"]
        tz["temp_定基"] = tz["定基增长率"] / 基准值
        tz = tz.loc[开始时间:]

        # 添加通胀列
        df["tz_等地位"] = df["hfq"] / tz["temp_定基"]

        # 通胀校准到当天
        基准值 = tz2.loc[开始时间, "定基增长率"]
        tz2["temp_定基"] = tz2["定基增长率"] / 基准值
        tz2 = tz2.loc[开始时间:]

        # 添加通胀列
        df["tz_等购买力"] = df["hfq"] / tz2["temp_定基"]

        # 日期转字符串
        # df["trade_date"] = df["trade_date"].astype(str)
        # df["trade_date"] = df["trade_date"].values.astype("U8")

        return code, df
    except Exception as e:
        print(f"读取股票 {code} 发生未知错误: {e}")
        return code, None


def get_all_股票数据(
    开始时间=1990101,
    start=["TS", "T", "300", "688", "301"],
    end=["BJ"],
    status=["D", "P", "G"],
):

    codes = get_股票列表(True)
    code_list = []
    for row in codes.itertuples():
        code = row.ts_code

        if row.name.startswith(("退市", "*ST", "ST")):
            continue

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

    tz = gp.tz.tz.__init_等地位_货币通胀()
    tz2 = gp.tz.tz.__init_等购买力_货币通胀()

    data_dict = {}
    print(f"开始加载 {len(code_list)} 只股票...")

    # 启动 joblib + loky 纯本地高速读取，12核拉满
    results = Parallel(n_jobs=10, backend="loky")(
        delayed(read_one)(code, 开始时间, tz, tz2) for code in code_list
    )

    # 完美过滤掉本地没有文件的 None 值
    data_dict = {k: v for k, v in results if v is not None}

    # print(f"成功合并了 {len(data_dict)} 只股票的数据")
    return data_dict


def get_后复权数据(股票数据列表):
    if not isinstance(股票数据列表, (list, tuple)):
        股票数据列表 = [股票数据列表]

    ret_data = []

    for df in 股票数据列表:
        # 冗余排序
        # df = df.copy()
        # df = df.sort_values(by="trade_date", ascending=True)

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
        ret_data.append(后复权数据)

    if len(ret_data) > 1:
        return ret_data
    else:
        return ret_data[0]
