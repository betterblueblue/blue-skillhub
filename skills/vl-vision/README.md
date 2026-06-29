# VL Vision

> 让不具备视觉能力的 LLM 也能识图

通用 VL 识图工具。调用外部视觉语言模型 API，为纯文本 LLM 补充图片理解能力。

## 核心特性

10 个预置 prompt 模板外加自定义 prompt，覆盖描述、OCR、布局分析、代码生成等场景。Provider 适配器模式目前支持硅基流动，可扩展到 OpenAI / Gemini / Qwen。CLI 手动调用与 Agent 自动调用都支持，目录批量扫描能并行处理。API 调用失败时会做 3 次线性退避重试，API Key 也支持自动查找。

## 快速开始

```bash
# 1. 配置 API Key
export SILICONFLOW_API_KEY=sk-your-key-here
# 或创建 .env 文件

# 2. 安装依赖
pip install requests

# 3. 分析图片
python vl_vision.py photo.png
```

## 使用示例

```bash
# 通用描述
python vl_vision.py photo.png

# OCR 文字提取
python vl_vision.py document.png --template ocr

# 自定义 prompt
python vl_vision.py ui.png --prompt "这个按钮的文案是什么"

# 批量分析
python vl_vision.py ./images/ --batch

# JSON 输出
python vl_vision.py photo.png --json
```

## 项目结构

```
vl-vision/
├── SKILL.md              # Skill 元数据、prompt 模板、agent 调用指南
├── README.md             # 本文件
├── vl_vision.py          # 主入口：CLI + 编程接口
├── config.py             # 配置管理（环境变量、.env）
└── providers/
    ├── __init__.py       # Provider 注册表
    ├── base.py           # 抽象基类 VLProvider
    └── siliconflow.py    # 硅基流动适配器
```

## License

MIT
