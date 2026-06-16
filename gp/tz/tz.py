import gp.tz.gdp
import gp.tz.m2
import gp.tz.r人口
import gp.tz.c财富集中
from functools import lru_cache


@lru_cache(maxsize=None)
def __init_等购买力_货币通胀(开始日期=19900201):
    m2 = gp.tz.m2.get_m2定基增长率(开始日期)
    gdp = gp.tz.gdp.get_gdp定基增长率(开始日期)

    通胀_df = (m2["temp_定基"] / gdp["temp_定基"]).to_frame(name="定基增长率")

    return 通胀_df


def get_等购买力_货币通胀(开始日期=20040101, 出生时间戳=None, 起始财富=None):
    df = __init_等购买力_货币通胀()

    基准值 = df.loc[开始日期, "定基增长率"]

    df["temp_定基"] = df["定基增长率"] / 基准值

    return df.loc[开始日期:]


@lru_cache(maxsize=None)
def __init_等地位_货币通胀(开始日期=19900201, 出生时间戳=None, 起始财富=None):
    # def get_等地位_货币通胀(开始日期="20040101"):
    """
    固定了自己是阶级是底层压抑者来简化计算
    按照近些年抖音的说法就是 力工梭哈、性压抑者、安卓人等

    货币稀释倍率 * 资源增长倍率 / 人口增长倍率 / 财富集中倍率  = 等地位缩水倍率

    货币稀释倍率 * 资源增长倍率 = 维持同地位实际资源量
    / 人口增长倍率 因为人多少分,少人多分
    / 财富集中倍率 因为底层的财富占比整体在下跌

    简单生命时间戳修复
    起始时间戳
    生命长度，随时间不同，变化
    生命结构，随时间和长度不同，变化
    总的就是当前时间戳应该占有多少比例

    简单的阶级修复
    起始阶级
    不同时间，不同阶级的数量
    不同时间，不同阶级占有财富比例的变化
    不同时间，阶级向其他阶级变化的概率
    """

    m2 = gp.tz.m2.get_m2定基增长率(开始日期)
    gdp = gp.tz.gdp.get_gdp定基增长率(开始日期)
    rk = gp.tz.r人口.get_人口定基增长率(开始日期)
    cf = gp.tz.c财富集中.get_财富集中定基率(开始日期, "top_01")

    # 计算动态定基倍率
    通胀_df = (m2["temp_定基"] / gdp["temp_定基"]).to_frame(name="定基增长率")

    # 地位稀释倍数
    通胀_df = (
        通胀_df["定基增长率"] * gdp["temp_定基"] / rk["temp_定基"] / cf["temp_定基"]
    ).to_frame(name="定基增长率")

    return 通胀_df


def get_等地位_货币通胀(开始日期=20040101, 出生时间戳=None, 起始财富=None):
    df = __init_等地位_货币通胀()

    基准值 = df.loc[开始日期, "定基增长率"]

    df["temp_定基"] = df["定基增长率"] / 基准值

    return df.loc[开始日期:]
