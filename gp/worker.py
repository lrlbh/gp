import os
import pandas as pd


def read_one(args):
    code, path = args
    file_path = os.path.join(path, f"{code}.csv")
    if not os.path.exists(file_path):
        return code, None
    try:
        df = pd.read_csv(file_path, encoding="utf_8_sig", engine="pyarrow")
    except:
        df = pd.read_csv(file_path, encoding="utf_8_sig")
    return code, df
