import time
import logging
import datetime

from colorama import Fore, Style

from pathlib import Path

from fastspider.config import config
from fastspider.utils._singleton import Singleton
from logging.handlers import TimedRotatingFileHandler


class CyberpunkFormatter(logging.Formatter):
    """Custom formatter to add a cyberpunk style to logger messages."""

    def __init__(self):
        super().__init__(datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        level_color = {
            logging.DEBUG: Fore.LIGHTCYAN_EX + Style.BRIGHT,
            logging.INFO: Fore.LIGHTGREEN_EX + Style.BRIGHT,
            logging.WARNING: Fore.LIGHTYELLOW_EX + Style.BRIGHT,
            logging.ERROR: Fore.LIGHTRED_EX + Style.BRIGHT,
        }

        log_color = level_color.get(record.levelno, Fore.WHITE)
        log_fmt = (
                Fore.LIGHTMAGENTA_EX + '[%(asctime)s]' + Fore.LIGHTBLUE_EX + '[%(name)s]' + log_color + '[%(levelname)s] ' + Fore.LIGHTCYAN_EX + 'File: %(filename)s → Func: %(funcName)s → Line:  %(lineno)d \n' + log_color + ">> " + log_color + " %(message)s" + Style.RESET_ALL)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


class LogManager(metaclass=Singleton):
    def __init__(self, logger: logging.Logger):
        if getattr(self, "_initialized", False):  # 防止重复初始化
            return
        self.logger = logger
        self.log_dir = None
        self._initialized = True

    def setup_logging(self, level=logging.INFO, log_to_console=False, log_path=None):
        self.logger.handlers.clear()
        formatter = CyberpunkFormatter()
        if log_to_console:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        if log_path:
            self.log_dir = Path(log_path)
            self.ensure_log_dir_exists(self.log_dir)
            log_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")
            log_file = self.log_dir.joinpath(log_file_name)
            fh = TimedRotatingFileHandler(
                log_file, when="midnight", interval=1, backupCount=99, encoding="utf-8"
            )
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    @staticmethod
    def ensure_log_dir_exists(log_path: Path):
        log_path.mkdir(parents=True, exist_ok=True)

    def clean_logs(self, keep_last_n=10):
        """保留最近的n个日志文件并删除其他文件"""
        if not self.log_dir:
            return
        # self.shutdown()
        all_logs = sorted(self.log_dir.glob("*.logger"))
        if keep_last_n == 0:
            files_to_delete = all_logs
        else:
            files_to_delete = all_logs[:-keep_last_n]
        for log_file in files_to_delete:
            try:
                log_file.unlink()
            except PermissionError:
                self.logger.warning(
                    f"无法删除日志文件 {log_file}, 它正被另一个进程使用"
                )

    def shutdown(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
        self.logger.handlers.clear()
        time.sleep(1)  # 确保文件被释放


def log_setup(log_to_console=True, level=logging.INFO):
    logger = logging.getLogger('FastSpider')
    logger.setLevel(level)
    if logger.hasHandlers():
        # logger已经被设置，不做任何操作
        return logger

    # 创建临时的日志目录
    temp_log_dir = Path("./logs")
    temp_log_dir.mkdir(exist_ok=True)

    # 初始化日志管理器
    log_manager = LogManager(logger)
    log_manager.setup_logging(
        level=level, log_to_console=log_to_console, log_path=temp_log_dir
    )

    # 只保留99个日志文件
    log_manager.clean_logs(99)

    return logger


if config.get_config('logger'):
    logger_cfg = config.get_config('logger')
    level = logger_cfg['level'].upper()
    log_to_console = logger_cfg['console']
    logger = log_setup(log_to_console=log_to_console, level=level)
else:
    logger = log_setup()
