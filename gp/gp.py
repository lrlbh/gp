import os.path
import time
import os
from pathlib import Path
import pandas as pd
import tl
import tl.dir
from datetime import datetime
import gp.pub
import gp.gdp
import gp.m2


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
        get_单个股票数据(code="000001.SZ", 强制更新=True)["trade_date"]
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
            data_list.append(get_单个股票数据(code))
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
    单个股票文件 = os.path.join(gp.pub.单个股票path, f"{code}.csv")

    # 获取数据
    if os.path.exists(单个股票文件) and not 强制更新:
        df = pd.read_csv(单个股票文件, encoding="utf_8_sig")
        return df

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


def get_all_股票数据(
    开始时间="20040101", start=["TS", "T"], end=["BJ"], status=["D", "P", "G"]
):
    if len(开始时间) == 4:
        开始时间 += "0101"
    elif len(开始时间) == 6:
        开始时间 += "01"

    data_list = []

    code_list = get_股票列表(True)

    for row in code_list.itertuples():
        code = row.ts_code

        # 部分股票没有数据，跳过
        # 部分股票代码,被回收复用,TS开头
        if code.startswith(tuple(start)):
            continue

        if code.endswith(tuple(end)):
            continue

        if row.list_status in status:
            continue

        # 获取后复权股票数据
        data = get_单个股票数据(code)
        data = data[data["trade_date"] > int(开始时间)].reset_index(drop=True)
        data_list.append(data)

    return data_list


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


def get_通胀修复数据(后复权数据):
    if not isinstance(后复权数据, (list, tuple)):
        后复权数据 = [后复权数据]

    # 获取通胀数据
    gdp = gp.gdp.get_gdp_补偿()
    m2 = gp.m2.get_m2_补偿()
    货币贬值 = {key: (m2[key] - gdp[key]) for key in m2}

    ret_data = []

    for data in 后复权数据:
        tz = data.copy()
        # 修复通胀
        上市第一天 = min(tz.keys())
        for key in tz:
            区间贬值 = 货币贬值[key] - 货币贬值[上市第一天]
            tz[key] /= 1 + 区间贬值

        ret_data.append(tz)

    if len(ret_data) > 1:
        return ret_data
    else:
        return ret_data[0]

    #     tz_list = list(tz.values())
    #     股票平均值 = sum(tz_list) / len(tz_list)
    #     股票当前值 = tz_list[-1]
    #     股票最小值 = min(tz_list)

    #     if 股票当前值 <= 股票最小值 * 1.0693:  # and 股票当前值 * 9 <= 股票平均值:
    #         if row.name.startswith(("S", "s", "*", "退")):
    #             异常_min_code_list.append(code)  # + "-->" + row.name)
    #         else:
    #             min_code_list.append(code)  # + "-->" + row.name)

    #             # 归一化(hfq)
    #             # 归一化(tz)
    #             # plt.title(row.name)
    #             # x_time = [datetime.strptime(date, "%Y%m%d") for date in hfq.keys()]
    #             # plt.plot(x_time, hfq.values(), color="green", label="后复权股价")
    #             # x_time = [datetime.strptime(date, "%Y%m%d") for date in tz.keys()]
    #             # plt.plot(x_time, tz.values(), color="red", label="通胀修复后股价")
    #             # plt.legend()
    #             # plt.show()
    # print(len(min_code_list))
    # print(min_code_list)


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
