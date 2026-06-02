import tl.pyboard
import tl.dir
import os


# 继承pyb
class Pyb(tl.pyboard.Pyboard):
    @staticmethod
    def 增量同步文件(
        com,
        path_list,
        分割符,
        波特率=115200,
        连接串口等待时间S=0,  # 没连接上串口触发
        独占串口=True,
        读超时S=3,  # 读取时超时时间,None阻塞等待
        写超时S=3,  # 写缓冲区满触发
    ):
        # 建立连接
        repl = Pyb(
            device=com,
            baudrate=波特率,
            wait=连接串口等待时间S,
            exclusive=独占串口,
            timeout=读超时S,
            write_timeout=写超时S,
        )

        # 出错也释放资源
        try:
            repl.enter_raw_repl()  # 进入非交互shell

            # 遍历文件列表,上传文件
            for file_name in path_list:
                py_file_name = file_name.split(分割符)
                if len(py_file_name) != 2:
                    raise Exception(f"文件分割后不是两个元素: {file_name}")

                # print(f"开始上传{py_file_name[1]}")
                repl.fs_force_put(file_name, py_file_name[1])

            repl.exit_raw_repl()  # 让开发板返回交互模式
        finally:  # finally不会拦截错误,会继续抛出原始错误
            try:
                repl.close()
            except Exception:
                pass

    # 在fs_put前调用,用于确保目录存在
    def fs_loop_dir(self, remote_path):
        """逐级创建远程文件的父目录"""
        remote_path = remote_path.replace("\\", "/").rstrip("/")
        if "/" in remote_path:
            dir_path = remote_path.rsplit("/", 1)[0]
        else:
            return
        if not dir_path:
            return

        parts = dir_path.split("/")
        current = ""
        for part in parts:
            if not part:
                continue
            current = current + "/" + part if current else part
            if not self.fs_exists(current):
                self.fs_mkdir(current)

    # 带目录创建的fs_put
    def fs_force_put(
        self, local_path, remote_path, chunk_size=256, progress_callback=None
    ):
        """上传文件，自动创建父目录"""
        remote_path = remote_path.replace("\\", "/")
        self.fs_loop_dir(remote_path)  # 只创建父目录
        self.fs_put(
            local_path, remote_path, chunk_size, progress_callback
        )  # 直接用原路径
