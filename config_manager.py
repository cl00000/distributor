# config_manager.py
import os
import json
from typing import Any, Dict
from pathlib import Path


class ConfigManager:
    """配置文件管理器"""

    def __init__(self):
        # 获取用户主目录下的配置路径，避免权限问题
        self.CONFIG_DIR = Path.home() / ".distributor_tool"
        self.CONFIG_PATH = self.CONFIG_DIR / "config.json"
        self._ensure_config_file()

    def _ensure_config_file(self):
        """确保配置文件存在"""
        # 创建配置目录（如果不存在）
        self.CONFIG_DIR.mkdir(exist_ok=True, parents=True)

        if not self.CONFIG_PATH.exists():
            # 创建默认配置
            default_config = {
                "window_position": [200, 200],
                "window_size": [260, 320],
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
            print(f"✅ 已创建默认配置文件: {self.CONFIG_PATH}")

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.CONFIG_PATH.exists():
                self._ensure_config_file()

            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ 已加载配置文件: {self.CONFIG_PATH}")
                return config
        except Exception as e:
            print(f"⚠ 加载配置文件失败: {e}，使用默认配置")
            # 返回默认配置
            return self._get_default_config()

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "window_position": [200, 200],
            "window_size": [260, 320],
            "settings": {
                "auto_start": False,
                "show_tips": True
            },
            "user_data": {
                "last_input": "",
                "favorite_coordinates": []
            }
        }

    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        try:
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"✅ 已保存配置文件: {self.CONFIG_PATH}")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")

    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        config = self.load_config()

        # 递归更新配置
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        config = deep_update(config, updates)
        self._save_config(config)

    def get_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.load_config()
        keys = key.split('.')
        value = config

        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception:
            return default

    def set_value(self, key: str, value: Any):
        """设置配置值"""
        config = self.load_config()
        keys = key.split('.')
        current = config

        # 遍历到最后一个键的父级
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                # 如果中间路径不是字典，替换为字典
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