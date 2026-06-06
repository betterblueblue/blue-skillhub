from .base import VLProvider
from .siliconflow import SiliconFlowProvider

PROVIDERS: dict[str, type[VLProvider]] = {
    "siliconflow": SiliconFlowProvider,
}


def get_provider(name: str) -> VLProvider:
    """根据名称获取 Provider 实例"""
    cls = PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"未知 Provider: {name}，可用: {list(PROVIDERS.keys())}")
    return cls()
