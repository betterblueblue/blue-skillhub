"""
单词海报出图脚本
读取 output/{word}/ 下的 prompt-*.txt 文件，调用生图 API 生成 9:16 海报图片并保存。

支持多个 Provider：
  grs   — GRS AI API（默认，异步轮询）
  yunwu — Yunwu AI（OpenAI 兼容格式，同步返回）

用法：
  python word-poster-generate.py output/孤独/              # 使用默认 provider
  python word-poster-generate.py output/孤独/ -p yunwu     # 指定 provider
  python word-poster-generate.py                           # 交互式选择
"""

import os
import sys
import time
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("请先安装 requests：pip install requests")
    sys.exit(1)

# ─── 加载 .env ───────────────────────────────────────────────────

ENV_PATH = Path(r"D:\MyPythonProject\image\.env")

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    else:
        print(f"警告：未找到 .env 文件：{ENV_PATH}")
        print("请确认 D:\\MyPythonProject\\image\\.env 存在并已填写 API Key")
        sys.exit(1)


# ─── 常量 ────────────────────────────────────────────────────────

POLL_INTERVAL = 5
MAX_POLL_TIME = 300

GRS_ASPECT_RATIO = "9:16"
YUNWU_SIZE = "1024x1792"

STYLE_MAP = {
    "float":      "悬浮",
    "stage":      "舞台",
    "deep":       "深度",
    "deep-bold":  "深度强调",
}


# ─── Provider: GRS ───────────────────────────────────────────────

def generate_grs(prompt: str) -> str:
    """GRS API：提交任务 → 轮询 → 返回图片 URL"""
    api_key = os.getenv("GRS_API_KEY", "")
    api_host = os.getenv("GRS_API_HOST", "https://grsai.dakka.com.cn")
    model = os.getenv("GRS_MODEL", "gpt-image-2")

    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError("GRS_API_KEY 未配置")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # 提交任务
    url = f"{api_host}/v1/draw/completions"
    payload = {
        "model": model,
        "prompt": prompt,
        "aspectRatio": GRS_ASPECT_RATIO,
        "webHook": "-1",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        raise RuntimeError(f"提交失败：{data.get('msg', '未知错误')}")

    task_id = data["data"]["id"]
    print(f"  任务已提交，ID: {task_id}")

    # 轮询结果
    result_url = f"{api_host}/v1/draw/result"
    start = time.time()
    while time.time() - start < MAX_POLL_TIME:
        resp = requests.post(result_url, headers=headers, json={"id": task_id}, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        if result.get("code") != 0:
            raise RuntimeError(f"查询失败：{result.get('msg', '未知错误')}")

        task = result.get("data", {})
        status = task.get("status", "")
        progress = task.get("progress", 0)

        if status == "succeeded":
            images = task.get("results", [])
            if not images:
                raise RuntimeError("生成成功但未返回图片")
            print(f"  生成完成")
            return images[0]["url"]
        elif status == "failed":
            reason = task.get("failure_reason", "未知原因")
            raise RuntimeError(f"生成失败：{reason} - {task.get('error', '')}")

        print(f"  进度: {progress}%", end="\r")
        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"等待超时（{MAX_POLL_TIME}秒）")


# ─── Provider: Yunwu ─────────────────────────────────────────────

def generate_yunwu(prompt: str) -> str:
    """Yunwu API（OpenAI 兼容）：同步返回图片 URL"""
    api_key = os.getenv("YUNWU_API_KEY", "")
    api_host = os.getenv("YUNWU_API_HOST", "https://yunwu.ai")
    model = os.getenv("YUNWU_MODEL", "gpt-image-2-all")

    if not api_key:
        raise RuntimeError("YUNWU_API_KEY 未配置")

    url = f"{api_host}/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": YUNWU_SIZE,
        "n": 1,
    }

    print(f"  请求中...")
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    images = data.get("data", [])
    if not images:
        raise RuntimeError("未返回图片")

    # OpenAI 格式：data[0].url 或 data[0].b64_json
    img = images[0]
    if "url" in img:
        print(f"  生成完成")
        return img["url"]
    elif "b64_json" in img:
        import base64
        print(f"  生成完成（base64）")
        return "b64://" + img["b64_json"]
    else:
        raise RuntimeError("响应中无图片 URL 或 base64 数据")


# ─── Provider 注册表 ──────────────────────────────────────────────

PROVIDERS = {
    "grs": generate_grs,
    "yunwu": generate_yunwu,
}


# ─── 通用逻辑 ─────────────────────────────────────────────────────

def download_image(image_url: str, save_path: str):
    """下载图片到本地（支持 b64:// 前缀的 base64 数据）"""
    if image_url.startswith("b64://"):
        import base64
        img_data = base64.b64decode(image_url[6:])
        with open(save_path, "wb") as f:
            f.write(img_data)
    else:
        resp = requests.get(image_url, timeout=60, stream=True)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"  已保存: {save_path}")


def parse_prompt_stem(stem: str) -> tuple[str, str]:
    """Parse prompt filename stem into (style, word).
    e.g. 'prompt-float-孤独' → ('float', '孤独')
    e.g. 'prompt-deep-bold-矛盾' → ('deep-bold', '矛盾')
    Also handles old format: 'prompt-float-raw' → ('float', 'raw')
    """
    rest = stem.replace("prompt-", "", 1)
    for style in ["deep-bold", "float", "stage", "deep"]:
        if rest.startswith(style + "-"):
            word = rest[len(style) + 1:]
            return style, word
    parts = rest.split("-", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def image_name_for_prompt(prompt_path: Path) -> str:
    """根据 prompt 文件名生成图片文件名：{中文风格}_{词语}.png"""
    style, word = parse_prompt_stem(prompt_path.stem)
    prefix = STYLE_MAP.get(style, style)
    return f"{prefix}_{word}.png"


def generate_for_word(word_dir: str, provider: str):
    """为指定单词目录生成图片"""
    word_path = Path(word_dir)
    if not word_path.is_dir():
        print(f"目录不存在：{word_dir}")
        return

    word = word_path.name

    # 读取 prompt-*.txt 文件，按文件名排序
    prompt_files = sorted(word_path.glob("prompt-*.txt"))
    if not prompt_files:
        print(f"未找到 prompt 文件：{word_dir}")
        return

    generate = PROVIDERS[provider]
    print(f"Provider: {provider}")
    print(f"单词: {word}")
    print(f"找到 {len(prompt_files)} 个 Prompt 文件")

    for pf in prompt_files:
        style, word = parse_prompt_stem(pf.stem)
        label = STYLE_MAP.get(style, style)
        print(f"\n--- {label} ({word}) ---")

        prompt_text = pf.read_text(encoding="utf-8").strip()
        if not prompt_text:
            print("  Prompt 为空，跳过")
            continue

        try:
            image_url = generate(prompt_text)
            save_name = image_name_for_prompt(pf)
            save_path = str(word_path / save_name)
            download_image(image_url, save_path)
        except Exception as e:
            print(f"  错误：{e}")
            continue


# ─── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="单词海报出图")
    parser.add_argument("word_dir", nargs="?", help="单词目录路径（如 output/孤独/）")
    parser.add_argument("-p", "--provider", default=os.getenv("DEFAULT_PROVIDER", "grs"),
                        choices=list(PROVIDERS.keys()), help="生图 Provider（默认: grs）")
    args = parser.parse_args()

    if args.word_dir:
        word_dir = args.word_dir
    else:
        output_dir = Path(__file__).parent / "output"
        if not output_dir.exists():
            print("output/ 目录不存在，请先运行 blue-word-poster skill 生成 prompt 文件")
            sys.exit(1)

        dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()])
        if not dirs:
            print("未找到任何单词目录")
            sys.exit(1)

        print("可用单词：")
        for i, d in enumerate(dirs, 1):
            prompt_count = len(list(d.glob("prompt-*.txt")))
            image_count = len(list(d.glob("*.png")))
            print(f"  {i}. {d.name}（{prompt_count} 个 Prompt，{image_count} 张图片）")

        choice = input("\n请输入序号（或直接输入目录路径）：").strip()
        try:
            idx = int(choice)
            word_dir = str(dirs[idx - 1])
        except (ValueError, IndexError):
            word_dir = choice

    generate_for_word(word_dir, args.provider)
    print("\n全部完成！")


if __name__ == "__main__":
    main()