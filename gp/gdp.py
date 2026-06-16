import os.path
import time
import os
from pathlib import Path
import pandas as pd
import tl
import tl.dir
from datetime import datetime
import gp.pub
from collections import deque
from functools import lru_cache


@lru_cache(maxsize=None)
def get_gdp(更新=False, 更新间隔S=60 * 60 * 24):
    # 是否需要更新
    if os.path.exists(gp.pub.gdp_path):
        # 获取最后修改时间戳
        最后修改时间戳 = datetime.fromtimestamp(
            Path(gp.pub.gdp_path).stat().st_mtime
        ).timestamp()

        if not 更新:
            df = pd.read_csv(gp.pub.gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

        if time.time() - 最后修改时间戳 < 更新间隔S:
            df = pd.read_csv(gp.pub.gdp_path, encoding="utf_8_sig")
            if len(df) >= 5999:
                print("WAR: GDP列表数据可能溢出了")
            return df

    # 获取数据
    print(f"更新GDP -> {gp.pub.gdp_path}")
    df = gp.pub.pro.cn_gdp(
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
    tl.dir.ensure_path_exists(gp.pub.gdp_path)
    df.to_csv(gp.pub.gdp_path, index=False, encoding="utf_8_sig")  # sig 带BOM的 UTF-8
    # print(f"数据已成功保存至: {gdp_path}")
    if len(df) >= 5999:
        print("WAR: GDP数据可能溢出了")

    return df


@lru_cache(maxsize=None)
def __init_gdp增长(开始日期="1989"):

    开始日期 = 开始日期[0:4]

    # 返回值
    ret = {}

    # 获取gdp数据
    df = get_gdp(True)

    # 第一年的GDP
    基值 = df[df["quarter"] == 开始日期 + "Q4"].gdp.item()

    # 增长倍率
    前4年倍率 = deque(maxlen=4)
    总年数 = int(datetime.now().strftime("%Y")) + 2 - int(开始日期)
    for i in range(总年数):
        当前年 = str(int(开始日期) + i)
        try:
            本年GDP = df.loc[df["quarter"] == 当前年 + "Q4", "gdp"].values[0]
        except IndexError:
            print(f"{当前年}年,GDP数据不存在,使用前三年平均增速预测")
            avg = 0
            for i in range(len(前4年倍率) - 1):
                avg += 前4年倍率[i + 1] / 前4年倍率[i]
            avg /= len(前4年倍率) - 1
            ret[当前年] = ret[str(int(当前年) - 1)] * avg
            前4年倍率.append(ret[当前年])
            continue

        ret[当前年] = 本年GDP / 基值
        前4年倍率.append(ret[当前年])

    # for key in ret:
    #     print(key, ret[key])

    # 2. 生成年份后，直接转换为该年的年末（YearEnd）
    dates = pd.to_datetime(list(ret.keys())) + pd.offsets.YearEnd(0)
    df = pd.DataFrame(list(ret.values()), index=dates, columns=["value"])

    # 3. 重新采样到“天”(D)，此时中间的日子会变成 NaN
    df_daily = df.resample("D").asfreq()

    # 4. 执行插值
    # 方法 A：线性插值（最稳妥，两点之间拉直线）
    df_daily["定基增长率"] = df_daily["value"].interpolate(method="linear")

    # 方法 B：三次样条插值（更平滑，适合金融曲线或自然增长，但注意两端可能会有轻微抖动）
    # df_daily["spline"] = df_daily["value"].interpolate(method="spline", order=3)

    # 自定义时间格式
    df_daily.index = df_daily.index.strftime("%Y%m%d").astype(int)

    # 截断数据，然数据只到今天
    df_daily = df_daily.loc[: int(datetime.now().strftime("%Y%m%d"))]
    # df_daily = df_daily.loc[:'20251231']

    return df_daily


def get_gdp定基增长率(开始日期=20040101):

    # 获取完整GDP增速
    df_daily = __init_gdp增长()

    # 转为从某一天开始的gdp增速
    新基准值 = df_daily.loc[开始日期, "定基增长率"]
    df_daily["temp_定基"] = df_daily["定基增长率"] / 新基准值

    # # # 5. 查看或导出结果
    # print("插值后的前 5 行数据：")
    # print(df_daily.head(5))

    # print("\n插值后的最后 5 行数据：")
    # print(df_daily.tail(5))

    return df_daily.loc[开始日期:]
