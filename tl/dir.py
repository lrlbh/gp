import sys
import importlib.util
import importlib

import binascii

import hashlib
from pathlib import Path
import os


def ensure_path_exists(file_path):
    """
    确保文件所在的目录存在。
    :param file_path: 完整的文件路径或目录路径
    """
    path = Path(file_path)

    # 如果传入的是文件路径，取其父目录；如果已经是目录，则直接处理
    # 也可以直接用 path.parent.mkdir
    path.parent.mkdir(parents=True, exist_ok=True)


# 返回完整路径列表
def get_files_path(path, 忽略=None):

    ret = []

    # 忽略的目录以及文件
    if 忽略 is None:
        忽略 = []

    # 将 ignore_list 转换为 set 提高查询效率
    ignore_set = set(忽略)

    for root, dirs, files in os.walk(path):
        # 1. 过滤目录 (原地修改 dirs，跳过不需要的子目录)
        # 这里的 [:] 是必须的，因为它允许我们在遍历的同时修改原列表
        dirs[:] = [d for d in dirs if d not in ignore_set]

        # 2. 过滤并处理文件
        for file in files:
            if file in ignore_set:
                continue

            # 构造完整路径
            file_path = os.path.join(root, file)
            file_path = os.path.normpath(file_path)
            ret.append(file_path)

    return ret


# 返回文件名称列表
def get_files_name(path, 忽略=None):
    # 1. 调用你现有的函数获取完整路径
    full_paths = get_files_path(path, 忽略=忽略)

    # 2. 遍历路径，提取最后一个层级（即文件名）
    # 使用列表推导式处理，简洁且高效
    filenames = [os.path.basename(p) for p in full_paths]

    return filenames

# print(get_files_name("C:\\Users\\82542\\code\\py\\MicroPython\\auto_shell"))


def get_files_md5(root_dir, ignore_list=None):
    """
    返回 {"/相对路径": MD5字符串}
    """
    if ignore_list is None:
        ignore_list = []
    ignore_set = set(ignore_list)
    result = {}

    def join_path(p1, p2):
        # 简单路径拼接
        if p1.endswith("/"):
            return p1 + p2
        else:
            return p1 + "/" + p2

    def is_file(path):
        try:
            return (os.stat(path)[0] & 0x4000) == 0  # 0x4000 表示目录
        except OSError:
            return False

    def walk(path, rel_prefix=""):
        try:
            items = os.listdir(path)
        except OSError:
            return

        for name in items:
            if name in ignore_set:
                continue

            full_path = join_path(path, name)
            rel_path = join_path(rel_prefix, name) if rel_prefix else name

            if is_file(full_path):
                # 计算MD5
                # s = time.ticks_ms()
                h = hashlib.md5()
                with open(full_path, "rb") as f:
                    h.update(f.read())
                key = "/" + rel_path.replace("\\", "/")
                result[key] = binascii.hexlify(h.digest()).decode()
                # print(key,time.ticks_ms()-s)
            else:
                walk(full_path, rel_path)

    walk(root_dir)
    return result


def import_path(file_path, register=False):
    """
    动态加载 Python 脚本作为配置模块

    :param file_path: .py 文件的绝对或相对路径
    :param register: 是否将该模块注册进 sys.modules (防止重复加载)
    :return: 模块对象，如果加载失败则返回 None
    """

    # 2. 自动生成模块名 (取文件名去掉后缀，例如 'config.py' -> 'config')
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # 3. 创建加载规格
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    # 4. 创建模块对象
    module = importlib.util.module_from_spec(spec)

    # 5. (可选) 注册到系统模块表，这能解决该配置脚本内部的相对导入问题dd
    if register:
        sys.modules[module_name] = module

    # 6. 执行脚本内容
    spec.loader.exec_module(module)

    return module
