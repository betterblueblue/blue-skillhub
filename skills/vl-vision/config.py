"""
vl-vision 配置管理

通过环境变量或 .env 文件配置，支持：
- VL_PROVIDER: 默认 Provider（默认 siliconflow）
- VL_MODEL: 默认模型（默认由 Provider 决定）
- SILICONFLOW_API_KEY: 硅基流动 API Key
"""

import os
from pathlib import Path


def load_env():
    """从 .env 文件加载环境变量（不覆盖已有值）"""
    current = Path.cwd()
    for _ in range(5):
        env_path = current / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            return
        parent = current.parent
        if parent == current:
            break
        current = parent


# 默认配置
DEFAULT_PROVIDER = "siliconflow"


def get_default_provider() -> str:
    """获取默认 Provider 名称"""
    return os.environ.get("VL_PROVIDER", DEFAULT_PROVIDER)


def get_default_model() -> str:
    """获取默认模型（由环境变量覆盖，否则由 Provider 决定）"""
    return os.environ.get("VL_MODEL", "")
