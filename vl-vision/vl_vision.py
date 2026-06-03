"""
vl-vision - 通用 VL 识图工具

让不具备视觉能力的 LLM 也能通过调用外部 VL API 识别图片。

用法：
    # 单图分析（使用默认 describe 模板）
    python vl_vision.py photo.png

    # 指定 prompt 模板
    python vl_vision.py photo.png --template ocr

    # 自定义 prompt（覆盖模板）
    python vl_vision.py photo.png --prompt "描述图中人物的穿着"

    # 批量分析目录
    python vl_vision.py ./images/ --batch

    # 指定模型
    python vl_vision.py photo.png --model Qwen/Qwen2.5-VL-72B-Instruct

    # JSON 输出
    python vl_vision.py photo.png --json

    # 列出可用模型
    python vl_vision.py --list-models
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# 确保可以 import 同级模块
sys.path.insert(0, str(Path(__file__).parent))

from config import load_env, get_default_provider, get_default_model
from providers import get_provider


# ─── Prompt 模板 ───

PROMPT_TEMPLATES = {
    # 描述型
    "describe": "请详细描述这张图片的内容，包括：主体、背景、色彩、文字、整体氛围。如实描述，不要遗漏重要细节。",
    "describe-scene": "请描述这个场景：空间布局、光照条件、天气或时间线索、前景中景远景的层次、整体氛围。忽略无关细节。",
    "describe-object": "请描述图中的主体物体：形状、材质、颜色、表面纹理、尺寸参照、品牌或标签信息。忽略背景。",
    "describe-people": "请描述图中的人物：外貌特征、面部表情、肢体姿态、服装配饰、动作意图、情绪状态。",
    "describe-art": "请从艺术角度分析这张图片：构图方式、色调搭配、风格流派、笔触或纹理、艺术手法、视觉冲击力。",
    # 任务型
    "ocr": "请完整提取图片中的所有文字，保持原始排版格式。如果文字模糊或有歧义，标注[模糊]。不要遗漏任何文字。",
    "layout": "请分析这张图片的布局结构：划分主要区域、标注各区域内容、描述元素排列方式和视觉层次。如果是 UI 截图，标注各组件位置。",
    "compare": "请对照以下预期，逐项检查图片内容是否匹配。对每个检查项给出：符合/不符合/无法判断，并说明依据。",
    "codegen": "请分析这张 UI 截图的结构，用文字描述如何用前端代码还原：1. 整体布局方案 2. 各区域组件 3. 关键样式属性 4. 交互逻辑。",
    "troubleshoot": "这张图片显示了报错或异常信息。请：1. 提取所有错误文字 2. 判断错误类型 3. 分析可能原因 4. 给出修复建议。",
}


def find_images(directory: str) -> list[str]:
    """扫描目录下的所有图片文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"错误: 目录不存在 - {directory}", file=sys.stderr)
        return []

    extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    images = [str(f) for f in sorted(dir_path.iterdir()) if f.suffix.lower() in extensions]
    return images


def resolve_prompt(args) -> str:
    """确定最终使用的 prompt（优先级：--prompt > --template > 默认 describe）"""
    if args.prompt:
        return args.prompt
    template_name = args.template or "describe"
    if template_name not in PROMPT_TEMPLATES:
        print(f"警告: 未知模板 '{template_name}'，使用默认 describe 模板", file=sys.stderr)
        template_name = "describe"
    return PROMPT_TEMPLATES[template_name]


def analyze_single(image_path: str, prompt: str, provider, model: str) -> dict:
    """分析单张图片，添加文件名和时间信息"""
    result = provider.analyze(image_path, prompt, model)
    result["image"] = Path(image_path).name
    result["timestamp"] = datetime.now().isoformat()
    return result


def format_text_output(results: list[dict], prompt: str) -> str:
    """格式化纯文本输出"""
    lines = []
    lines.append(f"## VL Vision 分析结果")
    lines.append(f"**Prompt**: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    lines.append(f"**图片数**: {len(results)}")
    lines.append("")

    for r in results:
        lines.append(f"### {r['image']}")
        if r["success"]:
            lines.append(r["description"])
        else:
            lines.append(f"**分析失败**: {r['error']}")
        lines.append("")

    return "\n".join(lines)


def format_json_output(results: list[dict], prompt: str) -> str:
    """格式化 JSON 输出"""
    output = {
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="vl-vision - 通用 VL 识图工具，让不具备视觉能力的 LLM 也能识图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
可用 Prompt 模板:
  描述型: {', '.join(t for t in PROMPT_TEMPLATES if not t.startswith(('ocr', 'layout', 'compare', 'codegen', 'troubleshoot')))}
  任务型: {', '.join(t for t in PROMPT_TEMPLATES if t.startswith(('ocr', 'layout', 'compare', 'codegen', 'troubleshoot')))}

示例:
  python vl_vision.py photo.png
  python vl_vision.py photo.png --template ocr
  python vl_vision.py photo.png --prompt "描述图中人物的穿着"
  python vl_vision.py ./images/ --batch
  python vl_vision.py photo.png --model Qwen/Qwen2.5-VL-72B-Instruct --json
        """,
    )
    parser.add_argument("image", nargs="?", help="图片文件路径或目录路径")
    parser.add_argument("--template", "-t", help="Prompt 模板名称")
    parser.add_argument("--prompt", "-p", help="自定义 prompt（覆盖模板）")
    parser.add_argument("--batch", "-b", action="store_true", help="批量模式：分析目录下所有图片")
    parser.add_argument("--provider", default=None, help="VL Provider（默认: siliconflow）")
    parser.add_argument("--model", "-m", default=None, help="模型标识")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--list-models", action="store_true", help="列出可用模型")
    parser.add_argument("--list-templates", action="store_true", help="列出可用 prompt 模板")

    args = parser.parse_args()

    # 加载 .env
    load_env()

    # 列出模板
    if args.list_templates:
        print("可用 Prompt 模板:\n")
        for name, prompt in PROMPT_TEMPLATES.items():
            print(f"  {name:20s} {prompt[:60]}...")
        return

    # 初始化 Provider
    provider_name = args.provider or get_default_provider()
    try:
        provider = get_provider(provider_name)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return

    # 列出模型
    if args.list_models:
        print(f"Provider: {provider.NAME}")
        print(f"默认模型: {provider.DEFAULT_MODEL}")
        if hasattr(provider, "AVAILABLE_MODELS"):
            print("\n可用模型:")
            for m in provider.AVAILABLE_MODELS:
                marker = " (默认)" if m == provider.DEFAULT_MODEL else ""
                print(f"  {m}{marker}")
        return

    # 必须提供图片参数
    if not args.image:
        parser.print_help()
        return

    # 确定 prompt
    prompt = resolve_prompt(args)

    # 确定模型
    model = args.model or get_default_model() or None

    # 收集图片
    image_path = Path(args.image)
    if args.batch and image_path.is_dir():
        images = find_images(args.image)
        if not images:
            print(f"目录下没有图片: {args.image}", file=sys.stderr)
            return
    elif image_path.is_dir():
        # 目录但未指定 --batch，提示用户
        images = find_images(args.image)
        if not images:
            print(f"目录下没有图片: {args.image}", file=sys.stderr)
            return
        if len(images) > 1:
            print(f"目录下有 {len(images)} 张图片，自动启用批量模式")
    else:
        if not image_path.exists():
            print(f"错误: 文件不存在 - {args.image}", file=sys.stderr)
            return
        images = [str(image_path)]

    print(f"Provider: {provider.NAME}")
    print(f"模型: {model or provider.DEFAULT_MODEL}")
    print(f"模板: {args.template or 'describe' if not args.prompt else '自定义'}")
    print(f"图片数: {len(images)}")
    print("-" * 50)

    # 分析图片
    results = []
    if len(images) == 1:
        result = analyze_single(images[0], prompt, provider, model)
        results.append(result)
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['image']}")
    else:
        # 并行分析（2 线程，避免 API 限流）
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(analyze_single, img, prompt, provider, model): img
                for img in images
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {result['image']}")

    # 按文件名排序
    results.sort(key=lambda r: r["image"])

    # 输出
    if args.json:
        print(format_json_output(results, prompt))
    else:
        print("-" * 50)
        print(format_text_output(results, prompt))


if __name__ == "__main__":
    main()
