"""
UserPromptSubmit hook — 拦阻用户直接粘贴图片到对话

背景:block-image-read.py 拦截的是 Read 工具读图片文件,但用户还可以
**直接把图片粘进对话**(附件通道,对话里显示为 [Image #N])。这条通道不走
Read 工具,PreToolUse 拦不到,图片会直接塞给主模型——纯文本模型(如
deepseek)不支持 vision,立即报 400 当前模型不支持该能力:vision。

本 hook 无条件拦截:只要用户消息带图片标记([Image),就阻断并引导改用
vl-vision(让模型转成 Read 图片路径 + vl-vision 调用,而不是直接粘图)。
不做任何模型名判断——是否启用由 settings.json 的挂载决定:
  - 当前用纯文本模型(如 deepseek)→ 挂上本 hook,粘图被拦
  - 当前用多模态模型(claude/gpt 等能看图)→ 摘掉本 hook(或换配置),直接粘图

设计原则:不做黑名单/白名单/模型判断(那是过度设计)。简单直接:
挂 hook = 拦,摘 hook = 放行。

退出码:0=放行 / 2=阻断(stderr 内容作为反馈回到会话)
"""

import json
import re
import sys
from pathlib import Path

# 图片附件在用户 prompt 里的标记(Claude Code 粘贴图片显示为 [Image #N])
_IMAGE_MARKER = re.compile(r"\[Image(?:\s+#\d+)?\]", re.IGNORECASE)

# vl_vision.py 在本文件同级的上一级(skills/vl-vision/vl_vision.py)
_VL_SCRIPT = str(Path(__file__).resolve().parent.parent / "vl_vision.py")


def guidance() -> str:
    return (
        "【阻断】不能直接把图片粘贴进对话:纯文本模型不支持 vision,图片附件会触发"
        " API 400,这是全局规则 CLAUDE.md 第 0 条明确禁止的。\n"
        "请改用 vl-vision skill 识图:\n"
        '  1. 把图片保存成文件,再让模型用 `python "'
        + _VL_SCRIPT
        + '" "图片路径" [--template ...]` 识别\n'
        "  2. 或直接告诉模型图片文件的路径,让它调用 vl-vision\n"
        "不要再直接粘贴图片。"
    )


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = data.get("prompt") or ""
    if not _IMAGE_MARKER.search(prompt):
        return 0  # 没有图片标记,放行

    sys.stderr.write(guidance() + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
