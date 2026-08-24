# VL Vision

> 为只支持文本的 AI 补充图片分析能力

VL Vision 会调用外部视觉语言模型 API，分析本地图片并返回文字结果。它适合 OCR、界面布局分析、图片描述和根据截图整理前端实现思路等任务。

## 核心特性

- 提供 10 个预置 Prompt，也支持完全自定义的 Prompt。
- 既能在命令行手动使用，也能由 AI 编码助手调用。
- 支持批量分析目录中的图片。
- API 调用失败时最多重试 3 次。
- 默认接入阶跃星辰（OpenAI 兼容），tokenrhythm 聚合网关、硅基流动作为备用渠道，也可以通过适配器增加其他服务。
- 内置识图门禁 hook：阻断不支持 vision 的模型直接 Read 图片，强制走 vl-vision（见 `hooks/README.md`）。

## 快速开始

```bash
# 1. 配置 API Key
export STEP_API_KEY=sk-your-stepfun-key
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
├── providers/
    ├── __init__.py       # Provider 注册表
    ├── base.py           # Provider 抽象基类
    ├── stepfun.py        # 阶跃星辰适配器（默认渠道）
    ├── tokenrhythm.py    # tokenrhythm 聚合网关适配器（备用渠道）
    └── siliconflow.py    # 硅基流动适配器（备用渠道）
└── hooks/
    ├── block-image-read.py # 识图门禁 PreToolUse hook（阻断不支持 vision 的模型直接 Read 图片）
    └── README.md           # hook 使用说明
```

## 配置门禁开关

内置识图门禁 hook **无条件拦截**（不做任何模型判断）。是否启用由你在
settings.json 里挂不挂决定：

- 当前接入**纯文本模型**（如 deepseek，不支持 vision）→ 挂上 hook，图片被拦、走 vl-vision
- 当前接入**多模态模型**（claude/gpt 等能看图）→ 不挂 hook，直接看图

不需要任何黑名单/白名单/环境变量开关。纯文本模型的完整配置示例见 `hooks/README.md`。

## 许可证

MIT
