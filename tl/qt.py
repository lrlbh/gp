import os
import webbrowser

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication

from datetime import datetime
import re
from PyQt6.QtCore import QTimer, QEventLoop
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QTextBlockFormat
from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtWidgets import QTextBrowser
import sys


def get_当前屏幕编号(widget):
    screens = QApplication.screens()

    # 获取窗口中心点（全局坐标）
    center = widget.frameGeometry().center()

    for i, screen in enumerate(screens):
        if screen.geometry().contains(center):
            return i
    return -1


def get_逻辑像素(index):
    """

    2. 获取指定编号屏幕的分辨率（逻辑像素）

    :param index: 屏幕编号

    :return: (width, height) 元组

    """
    screens = QApplication.screens()

    if 0 <= index < len(screens):
        target_screen = screens[index]

        # size() 返回的是考虑缩放后的逻辑分辨率

        # 如果需要真实的物理像素，建议使用 geometry()

        rect = target_screen.geometry()

        return rect.width(), rect.height()

    return None


def get_屏幕列表():
    # 获取当前所有屏幕的列表
    screens = QGuiApplication.screens()
    monitor_list = []

    for index, screen in enumerate(screens):
        info = {
            "index": index,
            "name": screen.name(),  # 操作系统识别的设备名
            "model": screen.model(),  # 显示器型号（可能为空）
            "manufacturer": screen.manufacturer(),  # 制造商
            "resolution": f"{screen.size().width()}x{screen.size().height()}",
            "refresh_rate": f"{screen.refreshRate()}Hz",
            "is_primary": screen == QGuiApplication.primaryScreen(),
            "device_pixel_ratio": screen.devicePixelRatio(),  # 缩放比例（如 1.25, 1.5, 2.0）
        }
        monitor_list.append(info)

    return monitor_list


# 移动ui到最下方
def set_当前屏幕_最下方(screen_index, w, h):
    # 1. 寻找主窗口 (保持原逻辑)
    main_widget = None
    for widget in QApplication.topLevelWidgets():
        if widget.isWindow() and widget.isVisible():
            main_widget = widget
            break

    if not main_widget:
        return

    screens = QGuiApplication.screens()
    if 0 <= screen_index < len(screens):
        screen = screens[screen_index]
        rect = screen.availableGeometry()  # 可用区域（已扣除任务栏）

        # 获取逻辑像素比例
        tw, th = get_逻辑像素(screen_index)
        target_w = int(w * tw)
        target_h = int(h * th)

        # --- 核心修正步骤 ---

        # A. 先设置大小
        main_widget.resize(target_w, target_h)

        # B. 先把窗口移到目标屏幕的左上角 (让 Qt 触发该屏幕的 DPI 适配)
        main_widget.move(rect.topLeft())

        # C. 强制处理挂起事件，让 Qt 刷新 frameGeometry
        QApplication.processEvents()

        # D. 现在计算 y 坐标才是准确的
        x = rect.left()
        # rect.bottom() 是底部边界坐标，减去当前窗口真实总高度
        y = rect.bottom() - main_widget.frameSize().height() + 1

        # 如果 frameSize() 仍不准，可以尝试使用：
        # y = rect.top() + rect.height() - main_widget.frameGeometry().height()

        main_widget.move(x, y)
        main_widget.show()
        main_widget.raise_()
        # main_widget.setMaximumWidth(target_w)


class log_widget(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setStyleSheet("background-color: black;")
        self.setReadOnly(True)
        self.msg = []
        self.setOpenExternalLinks(False)

        # 创建一个 QTextBlockFormat 对象并设置行间距
        # block_format = QTextBlockFormat()
        # block_format.setLineHeight(66, 2)  # 设置固定行高为20像素，1表示FixedHeight

        # 应用格式到整个文档
        # cursor = self.textCursor()
        # cursor.select(QTextCursor.SelectionType.Document)  # 选择整个文档
        # cursor.mergeBlockFormat(block_format)  # 合并块格式
        # self.setTextCursor(cursor)

        # 定时器
        timer = QTimer(self)

        # 定时器触发时执行的槽函数
        def timer_callback():
            while self.msg:
                data = self.msg.pop(0)
                self.__test(data[0], data[1], data[2])

        # 将槽函数与定时器的 timeout 信号连接
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(timer_callback)

        # 设置定时器的间隔，单位为毫秒
        timer.setInterval(100)

        # 启动定时器
        timer.start()

    def mousePressEvent(self, event):
        # 1. 获取点击位置的光标和文本块
        cursor = self.cursorForPosition(event.pos())
        full_text = cursor.block().text().strip()

        # 2. 使用正则表达式精准提取路径和行号
        # 匹配模式：查找 File "路径", line 行号
        pattern = r'File "(.*?)", line (\d+)'
        match = re.search(pattern, full_text)

        if match:
            file_path = match.group(1).replace("\\", "/")  # 统一斜杠
            line_num = match.group(2)
            webbrowser.open(f"vscode://file/{file_path}:{line_num}")
            # os.system(f'code -g "{file_path}:{line_num}"')

        # 记得调用父类方法，否则可能会影响默认行为（如滚动、选择）
        super().mousePressEvent(event)

    # 日志加上时间戳
    @staticmethod
    def __time_str(msg):
        now = datetime.now()
        return (
            f"{now.strftime('%H:%M:%S')}:{int(now.microsecond / 1000):03d} --> " + msg
        )

    # 更新日志框
    def __test(self, msg: str, font_size, 颜色):
        if not msg.endswith("\n"):
            msg += "\n"
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)  # 移动光标到文本末尾

        # 设置文本格式
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(颜色))
        font = QFont()  # 创建一个 QFont 对象
        font.setPointSize(font_size)  # 设置字体大小
        text_format.setFont(font)  # 将字体应用到格式中
        cursor.setCharFormat(text_format)

        # 插入带有格式的文本

        # 判断是否需要更新滚动条，如何插入日志
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            cursor.insertText(self.__time_str(msg))
            # 更新
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        else:
            cursor.insertText(self.__time_str(msg))

    def info(self, msg: str, font_size=24):
        self.msg.append((msg, font_size, "White"))

    def warning(self, msg: str, font_size=24):
        self.msg.append((msg, font_size, "yellow"))

    def error(self, msg: str, font_size=24):
        self.msg.append((msg, font_size, "red"))

    def ok(self, msg: str, font_size=24):
        self.msg.append((msg, font_size, "green"))

    def cyan(self, msg: str, font_size=24):
        self.msg.append((msg, font_size, "#00E5EE"))

    def all(self, msg: str, font_size=24):
        # font_size
        if msg.startswith("warning_lr"):
            _, msg = msg.split(" ", 1)
            self.warning(msg, font_size)
        elif msg.startswith("error_lr"):
            _, msg = msg.split(" ", 1)
            self.error(msg, font_size)
        elif msg.startswith("ok_lr"):
            _, msg = msg.split(" ", 1)
            self.ok(msg, font_size)
        else:
            self.info(msg, font_size)


class head:
    # 类属性：用于保存所有被装饰的函数引用
    _tasks = []
    # 类属性：用于保存所有函数运行后的结果
    widgets = []

    @classmethod
    def add(cls, func):
        """装饰器：将函数添加到任务列表中"""
        cls._tasks.append(func)
        return func

    @classmethod
    def load(cls):
        """运行所有函数并存入 d"""
        cls.widgets = [f() for f in cls._tasks]
        # return cls.widgets

    @classmethod
    def set_font_size(cls, font: QFont):
        for widget in cls.widgets:
            # 检查对象是否有 setFont 方法，防止非 QWidget 对象导致崩溃
            # if hasattr(widget, 'setFont'):
            widget.setFont(font)
