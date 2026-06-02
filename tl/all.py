import datetime


def time_str():
    """带时分秒毫秒的日志输出"""
    now = datetime.datetime.now()
    timestr = now.strftime("%H:%M:%S.%f")[:-3]
    return f"{timestr} > "
