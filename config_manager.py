# config_manager.py
import os
import json
from typing import Any, Dict


class ConfigManager:
    """配置文件管理器"""

    CONFIG_PATH = "C:/config.json"

    def __init__(self):
        self._ensure_config_file()

    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not os.path.exists(self.CONFIG_PATH):
            # 创建默认配置
            default_config = {
                "window_position": [100, 100],
                "window_size": [260, 388],
                "settings": {
                    "auto_start": False,
                    "show_tips": True
                },
                "user_data": {
                    "last_input": "",
                    "favorite_coordinates": []
                }
            }
            self._save_config(default_config)

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        try:
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        self._save_config(config)

    def get_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.load_config()
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set_value(self, key: str, value: Any):
        """设置配置值"""
        config = self.load_config()
        keys = key.split('.')
        current = config

        # 遍历到最后一个键的父级
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # 设置最终值
        current[keys[-1]] = value
        self._save_config(config)


# 创建全局配置管理器实例
config_manager = ConfigManager()


# 便捷函数
def load_config():
    return config_manager.load_config()


def save_config(config):
    config_manager._save_config(config)


def update_config(updates):
    config_manager.update_config(updates)


def get_config_value(key, default=None):
    return config_manager.get_value(key, default)


def set_config_value(key, value):
    config_manager.set_value(key, value)