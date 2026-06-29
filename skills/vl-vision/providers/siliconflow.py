"""
SiliconFlow VL Provider - 硅基流动视觉语言模型适配器

支持硅基流动平台上的 VL 模型（可用列表见下方 AVAILABLE_MODELS），
默认 Qwen/Qwen3-VL-32B-Instruct。

API 文档: https://docs.siliconflow.cn/
"""

import os
import time
from pathlib import Path

import requests

from .base import VLProvider


class SiliconFlowProvider(VLProvider):
    NAME = "siliconflow"
    DEFAULT_MODEL = "Qwen/Qwen3-VL-32B-Instruct"

    API_URL = "https://api.siliconflow.cn/v1/chat/completions"

    # 可用模型列表（供 --list-models 使用）
    AVAILABLE_MODELS = [
        "Qwen/Qwen3-VL-32B-Instruct",
        "Qwen/Qwen3-VL-32B-Thinking",
        "Qwen/Qwen3-VL-30B-A3B-Instruct",
        "Qwen/Qwen3-VL-30B-A3B-Thinking",
        "Qwen/Qwen3-VL-8B-Instruct",
        "Qwen/Qwen3-VL-8B-Thinking",
    ]

    def __init__(self):
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        """从环境变量或 .env 文件加载 API Key"""
        # 1. 环境变量
        key = os.environ.get("SILICONFLOW_API_KEY")
        if key:
            return key

        # 2. .env 文件（逐级向上查找）
        current = Path.cwd()
        for _ in range(5):
            env_path = current / ".env"
            if env_path.exists():
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("SILICONFLOW_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
            parent = current.parent
            if parent == current:
                break
            current = parent

        raise EnvironmentError(
            "未找到 SILICONFLOW_API_KEY。"
            "请设置环境变量或在 .env 文件中配置。"
        )

    def analyze(self, image_path: str, prompt: str, model: str = None) -> dict:
        """调用硅基流动 VL 模型分析图片"""
        model = model or self.DEFAULT_MODEL

        if not self.validate_image(image_path):
            return {
                "success": False,
                "error": f"图片文件无效: {image_path}",
                "model": model,
                "provider": self.NAME,
            }

        image_base64 = self.image_to_base64(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64,
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        }

        # 重试逻辑：3 次线性退避
        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                result = response.json()

                if "choices" in result:
                    return {
                        "success": True,
                        "description": result["choices"][0]["message"]["content"],
                        "model": model,
                        "provider": self.NAME,
                    }
                else:
                    # API 返回了错误。error 字段可能是 dict、str 或 null，
                    # 直接 .get("message") 会在非 dict 时抛 AttributeError，
                    # 被外层 except 吞掉后报给用户的是 Python 内部异常文本而非真实错误。
                    error = result.get("error")
                    if isinstance(error, dict):
                        error_msg = error.get("message", str(result))
                    elif error:
                        error_msg = str(error)
                    else:
                        error_msg = str(result)
                    return {
                        "success": False,
                        "error": f"API 错误: {error_msg}",
                        "model": model,
                        "provider": self.NAME,
                    }

            except requests.exceptions.Timeout:
                last_error = "请求超时"
                if attempt < max_retries:
                    time.sleep(5 * attempt)
            except requests.exceptions.ConnectionError:
                last_error = "连接失败"
                if attempt < max_retries:
                    time.sleep(5 * attempt)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "model": model,
                    "provider": self.NAME,
                }

        return {
            "success": False,
            "error": f"重试 {max_retries} 次后仍失败: {last_error}",
            "model": model,
            "provider": self.NAME,
        }
