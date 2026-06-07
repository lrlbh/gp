import os.path
import time
import os
from pathlib import Path
import pandas as pd
import tl
import tl.dir
import tushare as ts
from datetime import datetime


data_path = os.path.join(Path(__file__).resolve().parent, "data")  # 保存数据的路径
单个股票path = os.path.join(data_path, "单个股票")  # 单个股票数据的文件夹路径
股票列表path = os.path.join(data_path, "股票列表.csv")  # 股票列表的路径
gdp_path = os.path.join(data_path, "gdp.csv")
m2_path = os.path.join(data_path, "m2.csv")

# Tushare Pro 的 token
ts_token = "0e29e046df7990e93a881879bf0970f61aaa7cdaade91c97f4d6d412"
# 初始化 Tushare Pro 的 API
pro = ts.pro_api(ts_token)


def get_m2(更新=False, 更新间隔S=60 * 60 * 24):

    # 是否需要更新
    if os.path.exists(m2_path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(m2_path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(m2_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: M2列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(m2_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: M2列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新M2 -> {m2_path}")
    df = pro.cn_m(
        **{"m": "", "start_m": "", "end_m": "", "limit": "", "offset": ""},
        fields=[
            "month",
            "m0",
            "m0_yoy",
            "m0_mom",
            "m1",
            "m1_yoy",
            "m1_mom",
            "m2",
            "m2_yoy",
            "m2_mom",
        ],
    )

    # 写入到文件
    tl.dir.ensure_path_exists(m2_path)
    df.to_csv(m2_path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {m2_path}")
    if len(df) >= 5999:
        print("WAR: M2数据可能溢出了")

    return df


def get_gdp(更新=False, 更新间隔S=60 * 60 * 24):
    # 是否需要更新
    if os.path.exists(gdp_path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(gdp_path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新GDP -> {gdp_path}")
    df = pro.cn_gdp(
        **{"q": "", "start_q": "", "end_q": "", "limit": "", "offset": ""},
        fields=[
            "quarter",
            "gdp",
            "gdp_yoy",
            "pi",
            "pi_yoy",
            "si",
            "si_yoy",
            "ti",
            "ti_yoy",
        ],
    )

    # 写入到文件
    tl.dir.ensure_path_exists(gdp_path)
    df.to_csv(gdp_path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {gdp_path}")
    if len(df) >= 5999:
        print("WAR: GDP数据可能溢出了")

    return df


def get_gdp插值():
    df = get_gdp()

    # ========== 1. 创建完整的季度索引 ==========
    years = range(
        df["quarter"].str[:4].astype(int).min(),
        df["quarter"].str[:4].astype(int).max() + 1,
    )
    full_quarters = [f"{y}Q{q}" for y in years for q in range(1, 5)]

    df_full = pd.DataFrame({"quarter": full_quarters})
    df_full = df_full.merge(df, on="quarter", how="left")

    # ========== 2. 计算现代数据的平均季度比例 ==========
    modern = df_full[df_full["quarter"].str[:4].astype(int) >= 1992].copy()

    ratios = {}
    for col in ["gdp", "pi", "si", "ti"]:
        modern["year"] = modern["quarter"].str[:4].astype(int)
        modern["q"] = modern["quarter"].str[-1].astype(int)
        pivot = modern.pivot(index="year", columns="q", values=col)
        ratios[col] = {
            1: (pivot[1] / pivot[4]).mean(),
            2: (pivot[2] / pivot[4]).mean(),
            3: (pivot[3] / pivot[4]).mean(),
            4: 1.0,
        }

    # 比例示例：gdp 的 Q1≈21.0%, Q2≈44.7%, Q3≈69.8% 的 Q4
    # print("季度占Q4比例:", {k: {q: round(v, 4) for q, v in r.items()}
    #                     for k, r in ratios.items()})

    # ========== 3. 对早期只有Q4的年份进行拆分 ==========
    early_years = range(1952, 1992)

    for _, row in df_full.iterrows():
        year = int(row["quarter"][:4])
        q = int(row["quarter"][-1])

        if year in early_years and q == 4 and pd.notna(row["gdp"]):
            for target_q in [1, 2, 3]:
                target = f"{year}Q{target_q}"
                idx = df_full[df_full["quarter"] == target].index[0]
                for col in ["gdp", "pi", "si", "ti"]:
                    df_full.loc[idx, col] = row[col] * ratios[col][target_q]

    # ========== 4. 处理同比增长率（可选） ==========
    # 早期 Q1-Q3 没有去年同期，yoy 理论上应为 NaN
    # 如果你需要填充，可以用该年 Q4 的 yoy 近似（假设全年增速均匀）
    for _, row in df_full.iterrows():
        year = int(row["quarter"][:4])
        q = int(row["quarter"][-1])
        if year in early_years and q == 4:
            for target_q in [1, 2, 3]:
                target = f"{year}Q{target_q}"
                idx = df_full[df_full["quarter"] == target].index[0]
                for col in ["gdp_yoy", "pi_yoy", "si_yoy", "ti_yoy"]:
                    if pd.notna(row[col]):
                        df_full.loc[idx, col] = row[col]

    return df_full


def get_股票列表(更新=False, 更新间隔S=60):

    # 是否需要更新
    if os.path.exists(股票列表path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(股票列表path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(股票列表path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: 股票列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(股票列表path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: 股票列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新股票列表 -> {股票列表path}")
    df = pro.stock_basic(
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
    tl.dir.ensure_path_exists(股票列表path)
    df.to_csv(股票列表path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
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
        df = pro.daily(
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

            单个股票文件 = os.path.join(单个股票path, f"{code}.csv")
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
