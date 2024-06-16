import os
import sys
import signal
import asyncio

from fastspider.utils._singleton import Singleton
from fastspider.utils.console_manager import RichConsoleManager


class SignalManager(metaclass=Singleton):
    def __init__(self):
        self._shutdown_event = asyncio.Event()

    @property
    def shutdown_event(self):
        """提供对shutdown_event的只读访问"""
        return self._shutdown_event

    def shutdown(self):
        # 发送 SIGINT 信号给进程
        os.kill(os.getpid(), signal.SIGINT)

    def _handle_signal(self, received_signal, frame):
        """内部处理接收到的信号"""
        self._shutdown_event.set()
        RichConsoleManager().rich_console.print("exiting ...")
        # 取消所有运行中的asyncio任务
        for task in asyncio.all_tasks():
            task.cancel()

        # 执行资源清理操作
        sys.exit(0)

    def register_shutdown_signal(self):
        """注册一个处理程序来捕获关闭信号"""
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)  # 捕获SIGTERM信号，确保更好的跨平台兼容性

    @classmethod
    def is_shutdown_signaled(cls):
        """检查是否接收到了关闭信号"""
        instance = cls()  # 获取单例实例
        return instance.shutdown_event.is_set()

# 当需要的时候，就注册这个关闭信号
# signal_manager = SignalManager()
# signal_manager.register_shutdown_signal()
