"""
UserPromptSubmit hook — 阻断用户直接粘贴图片到对话

背景:block-image-read.py 拦截的是 Read 工具读图片文件,但用户还可以
**直接把图片粘进对话**(附件通道,对话里显示为 [Image #N])。这条通道不走
Read 工具,PreToolUse 拦不到,图片会直接塞给主模型——若主模型不支持
vision(如 deepseek-v4-flash),立即报 400 当前模型不支持该能力:vision。

本 hook 在用户提交消息时检测是否带图片标记([Image),有则阻断并引导改用
vl-vision。与 block-image-read.py 共用同一个判断(模型是否支持 vision):
  - 默认放行:正常多模态模型直接走 Claude Code 默认机制
  - 仅当模型名命中纯文本黑名单(如 deepseek-v4/v3)才阻断,提示改用 vl-vision
    (让模型转成 Read 图片路径 + vl-vision 调用,而不是直接粘图)

退出码:0=放行 / 2=阻断(stderr 内容作为反馈回到会话)
"""

import json
import os
import re
import sys
from pathlib import Path

# 纯文本模型黑名单——与 block-image-read.py 共读同一个黑名单,
# 避免两处各自维护一份(若黑名单文件读不到,用内置兜底,且默认放行)
_VL_SCRIPT = str(Path(__file__).resolve().parent.parent / "vl_vision.py")
_BLACKLIST = str(Path(__file__).resolve().parent / "vision_blacklist.json")

# 内置兜底关键词(黑名单文件缺失/损坏时使用;只含已知纯文本系列)
_FALLBACK_KEYWORDS = (
    "deepseek-v4",
    "deepseek-v3",
    "deepseek-r1",
    "deepseek-chat",
    "deepseek-reasoner",
)

# 图片附件在用户 prompt 里的标记(Claude Code 粘贴图片显示为 [Image #N])
_IMAGE_MARKER = re.compile(r"\[Image(?:\s+#\d+)?\]", re.IGNORECASE)


def model_supports_vision() -> bool:
    """判断当前模型是否支持 vision(与 block-image-read.py 相同的默认放行逻辑)"""
    explicit = os.environ.get("CLAUDE_MODEL_SUPPORTS_VISION", "").strip().lower()
    if explicit in ("1", "true", "yes", "on"):
        return True
    if explicit in ("0", "false", "no", "off"):
        return False
    model = (os.environ.get("ANTHROPIC_MODEL") or "").lower()
    if not model:
        return True  # 读不到模型名,默认放行
    # 读黑名单(与 block-image-read.py 共用),失败用内置兜底
    try:
        with open(_BLACKLIST, encoding="utf-8") as f:
            kws = json.load(f).get("keywords", [])
        keywords = tuple(k.lower() for k in kws) if isinstance(kws, list) else _FALLBACK_KEYWORDS
    except Exception:
        keywords = _FALLBACK_KEYWORDS
    return not any(k in model for k in keywords)


def guidance() -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "未知")
    return (
        "【阻断】不能直接把图片粘贴进对话:当前模型("
        + model
        + ")不支持 vision,图片附件会触发 API 400,"
        "这是全局规则 CLAUDE.md 第 0 条明确禁止的。\n"
        "请改用 vl-vision skill 识图:\n"
        '  1. 把图片保存成文件,再让模型用 `python "'
        + _VL_SCRIPT
        + '" "图片路径" [--template ...]` 识别\n'
        "  2. 或直接告诉模型图片文件的路径,让它调用 vl-vision\n"
        "不要再直接粘贴图片。若你的模型其实支持看图却被误拦,"
        "设环境变量 CLAUDE_MODEL_SUPPORTS_VISION=1 后重启会话即可放行。"
    )


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = data.get("prompt") or ""
    if not _IMAGE_MARKER.search(prompt):
        return 0  # 没有图片标记,放行

    if model_supports_vision():
        return 0  # 模型能"亲眼看",放行

    sys.stderr.write(guidance() + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
