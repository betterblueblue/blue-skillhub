"""
PreToolUse hook — 阻断不支持 vision 的模型直接 Read 图片文件

背景:全局规则 CLAUDE.md 第 0 条要求识图必须走 vl-vision skill,
禁止用模型自身能力直接"看"图。但规则只靠模型自觉执行,弱模型
(如 deepseek-v4-flash)看到图片时本能走 Read 工具,把图片塞给主模型,
而该模型不支持 vision,API 直接报 400 卡死(典型表现:会话结尾
"API Error: 400 当前模型不支持该能力:vision" + 长时间死循环)。

本 hook 在 Read 工具调用前拦截图片文件,判断顺序:
  1. 显式开关 CLAUDE_MODEL_SUPPORTS_VISION
     (=1/true/yes/on 放行,=0/false/no/off 强制阻断)
  2. 未设开关 → 按模型名白名单兜底(claude/gemini/gpt-4o/qwen-vl/... 自动放行)
  3. 都拿不准 → 阻断(安全优先),引导改用 vl-vision

安装/配置/卸载说明见同目录 README.md;settings.json 的 hooks 块指向本文件。
退出码:0=放行 / 2=阻断(stderr 内容作为反馈回到模型上下文)

注意:本文件位于 skills/vl-vision/hooks/ 下,vl_vision.py 路径用相对路径推导,
skill 整体搬目录后无需改路径。
"""

import json
import os
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico"}

# 白名单配置文件与本脚本同目录(相对脚本位置推导,skill 搬家不用改)。
# 缺文件/损坏时按空白名单处理——相当于全部模型都不支持 vision,安全优先(宁误拦不放行)。
WHITELIST_FILE = str(Path(__file__).resolve().parent / "vision_whitelist.json")


def load_whitelist() -> tuple[str, ...]:
    """从 vision_whitelist.json 读取白名单关键词;失败返回空(安全降级)。"""
    try:
        with open(WHITELIST_FILE, encoding="utf-8") as f:
            data = json.load(f)
        keywords = data.get("keywords", [])
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            return tuple(k.lower() for k in keywords)
        print(f"[vl-vision hook] 警告: {WHITELIST_FILE} keywords 字段格式不对,按空白名单处理", file=sys.stderr)
        return ()
    except FileNotFoundError:
        print(f"[vl-vision hook] 警告: 找不到白名单文件 {WHITELIST_FILE},按空白名单处理", file=sys.stderr)
        return ()
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        print(f"[vl-vision hook] 警告: 读取白名单 {WHITELIST_FILE} 失败({e}),按空白名单处理", file=sys.stderr)
        return ()


VISION_MODEL_KEYWORDS = load_whitelist()

# vl_vision.py 在本文件同级的上一级(skills/vl-vision/vl_vision.py)
VL_SCRIPT = str(Path(__file__).resolve().parent.parent / "vl_vision.py")


def model_supports_vision() -> bool:
    """判断当前模型是否明确支持 vision。

    判断顺序(显式优先,白名单兜底):
      1. 环境变量 CLAUDE_MODEL_SUPPORTS_VISION
         =1/true/yes/on  → 放行(换多模态模型时手动设,不靠猜)
         =0/false/no/off → 阻断(强制)
      2. 未设置 → 按模型名白名单关键词兜底
      3. 都拿不准(无开关、名字不在白名单)→ 按不支持处理(安全优先)
    """
    explicit = os.environ.get("CLAUDE_MODEL_SUPPORTS_VISION", "").strip().lower()
    if explicit in ("1", "true", "yes", "on"):
        return True
    if explicit in ("0", "false", "no", "off"):
        return False
    model = (os.environ.get("ANTHROPIC_MODEL") or "").lower()
    if not model:
        return False
    return any(kw in model for kw in VISION_MODEL_KEYWORDS)


def guidance(path: str) -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "未知")
    return (
        "【阻断】不能直接 Read 图片文件:当前模型("
        + model
        + ")不支持 vision,直接读取会触发 API 400,"
        "这是全局规则 CLAUDE.md 第 0 条明确禁止的。\n"
        "请改用 vl-vision skill 识图:\n"
        '  python "'
        + VL_SCRIPT
        + '" "'
        + path
        + '" [--template describe|ocr|layout|codegen|troubleshoot] '
        '[--prompt "..."] [--json]\n'
        "识图结果以返回的 description 为准;若 vl-vision 失败,把错误告知用户,"
        "不要自行 Read 图片。\n"
        "—— 如果你的模型其实支持看图却被误拦,请用户设置环境变量 "
        "CLAUDE_MODEL_SUPPORTS_VISION=1 后重启会话即可放行。"
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

    if model_supports_vision():
        return 0  # 模型能"亲眼看",放行

    sys.stderr.write(guidance(path_str) + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
