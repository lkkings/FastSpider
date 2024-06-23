# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/15 19:03
@Author     : lkkings
@FileName:  : config.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import os.path

import yaml
import fastspider

from pathlib import Path
from fastspider.exceptions import (
    FileNotFound,
    FilePermissionError,
)
from fastspider.utils._singleton import Singleton
from fastspider.utils.file_utils import get_resource_path


class ConfigManager(metaclass=Singleton):
    # 如果不传入应用配置路径，则返回项目配置 (If the application conf path is not passed in, the project conf is returned)
    def __init__(self, filepath: str = None):
        if not filepath:
            self.filepath = os.path.join(os.getcwd(), 'conf.yaml')
        elif Path(filepath).exists():
            self.filepath = Path(filepath)
        else:
            self.filepath = Path(get_resource_path('default.yaml'))
        self.config = self.load_config()

    def load_config(self) -> dict:
        """从文件中加载配置 (Load the conf from the file)"""

        if not self.filepath.exists():
            raise FileNotFound("配置文件不存在", self.filepath)

        return yaml.safe_load(self.filepath.read_text(encoding="utf-8")) or {}

    def get_config(self, key: str, default=None) -> dict:
        """
        从配置中获取给定键的值 (Get the value of the given key from the conf)

        Args:
            key: str: 获取键值
            default: any: 默认值 (default value)

        Return:
            self.config.get 配置字典 (conf dict)
        """

        return self.config.get(key, default)

    def save_config(self, config: dict):
        """将配置保存到文件 (Save the conf to the file)
        Args:
            config: dict: 配置字典 (conf dict)
        """
        try:
            self.filepath.write_text(yaml.dump(config), encoding="utf-8")
        except PermissionError:
            raise FilePermissionError(self.filepath)

    def backup_config(self):
        """在进行更改前备份配置文件 (Backup the conf file before making changes)"""
        # 如果已经是备份文件，直接返回 (If it is already a backup file, return directly)
        if self.filepath.suffix == ".bak":
            return

        backup_path = self.filepath.with_suffix(".bak")
        if backup_path.exists():
            backup_path.unlink()  # 删除已经存在的备份文件 (Delete existing backup files)
        self.filepath.rename(backup_path)

    def generate_config(self, save_path: Path):
        """生成应用程序特定配置文件 (Generate application-specific conf file)"""

        # 将save_path转换为Path对象
        save_path = Path(save_path)

        # 如果save_path是相对路径，则将其转换为绝对路径
        if not save_path.is_absolute():
            save_path = Path.cwd() / save_path

        # 确保目录存在，如果不存在则创建
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取默认配置
        default_config = (
                yaml.safe_load(
                    Path(get_resource_path(fastspider.DEFAULTS_FILE_PATH)).read_text(
                        encoding="utf-8"
                    )
                )
                or {}
        )
        save_path.write_text(yaml.dump(default_config), encoding="utf-8")

    def update_config_with_args(self, key: str, **kwargs):
        """
        使用提供的参数更新配置 (Update the conf with the provided parameters)

        Args:
            key: str: 键
            kwargs: dict: 配置字典 (conf dict)
        """

        app_config = self.config.get(key, {})

        # 使用提供的参数更新特定应用的配置
        for _key, value in kwargs.items():
            if value is not None:
                app_config[_key] = value

        self.config[key] = app_config
        # 备份原始配置文件
        self.backup_config()
        # 保存更新的配置 (Save the updated conf)
        self.save_config(self.config)


class TestConfigManager:
    # 返回传入app的测试配置内容 (Return the test2 conf content passed in app)

    @classmethod
    def get_test_config(cls, key: str) -> dict:
        return ConfigManager(fastspider.TEST_CONFIG_FILE_PATH).get_config(key)



config = ConfigManager(filepath=_config_path)
