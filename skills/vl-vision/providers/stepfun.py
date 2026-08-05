"""
StepFun VL Provider - 阶跃星辰视觉语言模型适配器

阶跃星辰 API 为 OpenAI Chat Completions 兼容协议(base_url https://api.stepfun.com/step_plan/v1)。
默认模型 step-3.7-flash(原生多模态,支持图片理解),可用 VL_MODEL 环境变量覆盖。

API 文档: 见阶跃星辰开放平台接入说明(OpenAI Chat Completions 协议)
"""

import os
import time

import requests

from .base import VLProvider


class StepFunProvider(VLProvider):
    NAME = "stepfun"
    DEFAULT_MODEL = "step-3.7-flash"
    DEFAULT_BASE_URL = "https://api.stepfun.com/step_plan/v1"

    def __init__(self):
        self.base_url = self.DEFAULT_BASE_URL
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        """从环境变量加载 API Key(仅环境变量,不写死、不双读 .env)"""
        key = os.environ.get("STEP_API_KEY")
        if key:
            return key

        raise EnvironmentError(
            "未找到 STEP_API_KEY。"
            "请在环境变量中设置该值(vl-vision 的 load_env() 会统一加载 .env 到环境变量)。"
        )

    def analyze(self, image_path: str, prompt: str, model: str = None) -> dict:
        """调用阶跃星辰 VL 模型分析图片(OpenAI Chat Completions 协议)"""
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

        # 重试逻辑:3 次线性退避(与 tokenrhythm/siliconflow 一致)
        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
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
                    # API 返回了错误。error 字段可能是 dict、str 或 null,
                    # 直接 .get("message") 会在非 dict 时抛 AttributeError,
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
