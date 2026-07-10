# VL Vision

> 为只支持文本的 AI 补充图片分析能力

VL Vision 会调用外部视觉语言模型 API，分析本地图片并返回文字结果。它适合 OCR、界面布局分析、图片描述和根据截图整理前端实现思路等任务。

## 核心特性

- 提供 10 个预置 Prompt，也支持完全自定义的 Prompt。
- 既能在命令行手动使用，也能由 AI 编码助手调用。
- 支持批量分析目录中的图片。
- API 调用失败时最多重试 3 次。
- 当前内置硅基流动 Provider，也可以通过适配器增加其他服务。

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

# 自定义 Prompt
python vl_vision.py ui.png --prompt "这个按钮的文案是什么"

# 批量分析
python vl_vision.py ./images/ --batch

# JSON 输出
python vl_vision.py photo.png --json
```

## 项目结构

```
vl-vision/
├── SKILL.md              # Skill 元数据、Prompt 模板和调用说明
├── README.md             # 本文件
├── vl_vision.py          # 主入口：CLI + 编程接口
├── config.py             # 配置管理（环境变量、.env）
└── providers/
    ├── __init__.py       # Provider 注册表
    ├── base.py           # Provider 抽象基类
    └── siliconflow.py    # 硅基流动适配器
```

## 许可证

MIT
