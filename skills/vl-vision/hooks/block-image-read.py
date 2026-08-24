"""
PreToolUse hook — 拦阻直接 Read 图片文件

背景:全局规则 CLAUDE.md 第 0 条要求识图必须走 vl-vision skill,禁止用模型
自身能力直接"看"图。纯文本模型(如 deepseek)直接 Read 图片会触发 API 400
("当前模型不支持该能力:vision")并死循环。

本 hook 无条件拦截:只要 Read 目标是图片文件,就阻断并引导改用 vl-vision。
不做任何模型名判断——是否启用由 settings.json 的挂载决定:
  - 当前用纯文本模型(如 deepseek)→ 挂上本 hook,Read 图片被拦、走 vl-vision
  - 当前用多模态模型(claude/gpt 等能看图)→ 摘掉本 hook(或换配置),直接看图

设计原则:不做黑名单/白名单/模型判断(那是过度设计)。简单直接:
挂 hook = 拦,摘 hook = 放行。

安装/配置/卸载说明见同目录 README.md;settings.json 的 hooks 块指向本文件。
退出码:0=放行 / 2=阻断(stderr 内容作为反馈回到模型上下文)

注意:本文件位于 skills/vl-vision/hooks/ 下,vl_vision.py 路径用相对路径推导,
skill 整体搬目录后无需改路径。
"""

import json
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico"}

# vl_vision.py 在本文件同级的上一级(skills/vl-vision/vl_vision.py)
VL_SCRIPT = str(Path(__file__).resolve().parent.parent / "vl_vision.py")


def guidance(path: str) -> str:
    return (
        "【阻断】不能直接 Read 图片文件:纯文本模型不支持 vision,直接读取会触发"
        " API 400,这是全局规则 CLAUDE.md 第 0 条明确禁止的。\n"
        "请改用 vl-vision skill 识图:\n"
        '  python "'
        + VL_SCRIPT
        + '" "'
        + path
        + '" [--template describe|ocr|layout|codegen|troubleshoot] '
        '[--prompt "..."] [--json]\n'
        "识图结果以返回的 description 为准;若 vl-vision 失败,把错误告知用户,"
        "不要自行 Read 图片。"
    )


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # 解析失败不阻断,避免 hook 自身出错卡住工作流

    if data.get("tool_name") != "Read":
        return 0

    tool_input = data.get("tool_input") or {}
    path_str = tool_input.get("file_path") or tool_input.get("path") or ""
    if not path_str:
        return 0

    if Path(path_str).suffix.lower() not in IMAGE_EXTENSIONS:
        return 0

    sys.stderr.write(guidance(path_str) + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
