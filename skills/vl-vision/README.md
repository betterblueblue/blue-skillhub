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

内置识图门禁 hook 用环境变量 `CLAUDE_MODEL_SUPPORTS_VISION` 手动控制放行/阻断，优先于模型名白名单：

| 值 | 行为 |
|----|------|
| `1` / `true` / `yes` / `on` | 放行，允许直接 Read 图片（换白名单外的多模态模型时用） |
| `0` / `false` / `no` / `off` | 强制阻断，一律走 vl-vision |
| 不设置 | 按模型名白名单兜底（主流多模态模型名自动放行） |

```bash
# 在全局 settings.json 的 env 段加（推荐）或系统环境变量设置，重启会话生效：
export CLAUDE_MODEL_SUPPORTS_VISION=1
```

完整安装/配置/卸载说明见 `hooks/README.md`。

## 许可证

MIT
