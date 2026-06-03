"""
VLProvider - 视觉语言模型适配器抽象基类

所有平台适配器必须继承此类并实现 analyze() 方法。
"""

from abc import ABC, abstractmethod
from pathlib import Path


class VLProvider(ABC):
    """视觉语言模型 Provider 抽象基类"""

    # 子类必须设置
    NAME: str = ""          # Provider 名称（如 "siliconflow"）
    DEFAULT_MODEL: str = "" # 默认模型标识

    @abstractmethod
    def analyze(self, image_path: str, prompt: str, model: str = None) -> dict:
        """
        分析单张图片

        Args:
            image_path: 图片文件路径
            prompt: 分析提示词
            model: 模型标识（None 则使用默认模型）

        Returns:
            {
                "success": bool,
                "description": str,   # 成功时：VL 模型的分析结果
                "error": str,         # 失败时：错误信息
                "model": str,         # 实际使用的模型
                "provider": str       # Provider 名称
            }
        """
        ...

    def validate_image(self, image_path: str) -> bool:
        """校验图片文件是否存在且格式受支持"""
        path = Path(image_path)
        if not path.exists():
            return False
        if not path.is_file():
            return False
        return path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif")

    def image_to_base64(self, image_path: str) -> str:
        """将图片文件转为 base64 data URI"""
        import base64

        with open(image_path, "rb") as f:
            data = f.read()

        ext = Path(image_path).suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime = mime_map.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"
