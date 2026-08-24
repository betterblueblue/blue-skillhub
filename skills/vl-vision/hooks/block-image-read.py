"""
PreToolUse hook — 拦阻纯文本模型直接 Read 图片文件

背景:全局规则 CLAUDE.md 第 0 条要求识图必须走 vl-vision skill,禁止用模型
自身能力直接"看"图。但规则只靠模型自觉执行,纯文本模型(如 deepseek-v4-flash)
看到图片时本能走 Read 工具,把图片塞给主模型,而该模型不支持 vision,
API 直接报 400 卡死(典型表现:会话结尾 "API Error: 400 当前模型不支持
该能力:vision" + 长时间死循环)。

本 hook 在 Read 工具调用前拦截图片文件,判断逻辑(默认放行,只拦纯文本):
  1. 显式开关 CLAUDE_MODEL_SUPPORTS_VISION
     =1/true/yes/on  → 放行(强制)
     =0/false/no/off → 阻断(强制,一般不设)
  2. 未设开关 → 按模型名黑名单兜底(vision_blacklist.json 里的纯文本模型
     如 deepseek-v4/v3 等命中则拦);不命中 → 默认放行
  3. 读不到模型名 → 默认放行(不误伤正常多模态)

设计原则:正常多模态模型直接走 Claude Code 默认机制(能看图就自己看),
只有确认是纯文本模型的才拦,引导改用 vl-vision。这样换新模型不会被误拦。

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

# 黑名单配置文件与本脚本同目录(相对脚本位置推导,skill 搬家不用改)。
# 缺文件/损坏时按空黑名单处理——相当于全部放行(默认走正常机制,安全)。
BLACKLIST_FILE = str(Path(__file__).resolve().parent / "vision_blacklist.json")


def load_blacklist() -> tuple[str, ...]:
    """从 vision_blacklist.json 读取纯文本模型黑名单;失败返回空(默认放行)。"""
    try:
        with open(BLACKLIST_FILE, encoding="utf-8") as f:
            data = json.load(f)
        keywords = data.get("keywords", [])
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            return tuple(k.lower() for k in keywords)
        print(f"[vl-vision hook] 警告: {BLACKLIST_FILE} keywords 字段格式不对,按空黑名单处理", file=sys.stderr)
        return ()
    except FileNotFoundError:
        print(f"[vl-vision hook] 警告: 找不到黑名单文件 {BLACKLIST_FILE},按空黑名单处理", file=sys.stderr)
        return ()
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        print(f"[vl-vision hook] 警告: 读取黑名单 {BLACKLIST_FILE} 失败({e}),按空黑名单处理", file=sys.stderr)
        return ()


TEXT_MODEL_KEYWORDS = load_blacklist()

# vl_vision.py 在本文件同级的上一级(skills/vl-vision/vl_vision.py)
VL_SCRIPT = str(Path(__file__).resolve().parent.parent / "vl_vision.py")


def model_supports_vision() -> bool:
    """判断当前模型是否支持 vision。

    判断逻辑(默认放行,只拦纯文本):
      1. 环境变量 CLAUDE_MODEL_SUPPORTS_VISION
         =1/true/yes/on  → 放行(强制)
         =0/false/no/off → 阻断(强制,一般不设)
      2. 未设置 → 模型名命中黑名单(纯文本)→ 不支持;不命中 → 支持(默认放行)
      3. 读不到模型名 → 按支持处理(默认放行)
    """
    explicit = os.environ.get("CLAUDE_MODEL_SUPPORTS_VISION", "").strip().lower()
    if explicit in ("1", "true", "yes", "on"):
        return True
    if explicit in ("0", "false", "no", "off"):
        return False
    model = (os.environ.get("ANTHROPIC_MODEL") or "").lower()
    if not model:
        return True  # 读不到模型名,默认放行
    return not any(kw in model for kw in TEXT_MODEL_KEYWORDS)


def guidance(path: str) -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "未知")
    return (
        "【阻断】不能直接 Read 图片文件:当前模型("
        + model
        + ")是纯文本模型,不支持 vision,直接读取会触发 API 400,"
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
        return 0  # 默认放行,模型能"亲眼看"

    sys.stderr.write(guidance(path_str) + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
