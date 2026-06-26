---
name: vl-vision
description: >
  Utility tool — 通用 VL 识图工具（非核心 Skill）。调用外部视觉语言模型 API，让不具备视觉能力的 LLM 也能识别和理解图片。
  不参与 Skill 评测体系，不作为变更影响分析工具使用。仅在 agent 工作流中需要"看懂"图片时按需调用。
disable-model-invocation: true
---

# VL Vision — 识图工具（Utility）

> **定位**：本工具是 utility，不是核心 Skill（pathfinder / impact / triage 等的同类）。
> 不参与 Skill 评测体系的 L0/L1/L2 评测，不纳入变更影响分析流程。
> 仅在 agent 遇到图片处理需求时按需调用。

## 适用场景

- 当前 LLM 不支持图片输入（如 Llama、Qwen 文本版等）
- 需要对本地图片进行分析、描述、OCR、布局识别等
- Agent 工作流中需要"看懂"图片后继续文本任务

## 调用方式

```bash
python vl_vision.py <图片路径> [--template 模板名] [--prompt 自定义提示词] [--model 模型] [--json]
```

### 基本用法

```bash
# 单图通用描述
python vl_vision.py photo.png

# 使用指定模板
python vl_vision.py screenshot.png --template ocr

# 自定义 prompt（最高优先级）
python vl_vision.py photo.png --prompt "判断图中是否有猫"

# 批量分析目录
python vl_vision.py ./images/ --batch

# JSON 格式输出（便于程序解析）
python vl_vision.py photo.png --json

# 指定模型
python vl_vision.py photo.png --model Qwen/Qwen2.5-VL-72B-Instruct

# 查看可用模板
python vl_vision.py --list-templates

# 查看可用模型
python vl_vision.py --list-models
```

## Prompt 模板

预置两类共 10 个模板。使用 `--template` 指定，也可用 `--prompt` 完全自定义。

### 描述型模板

回答"图里有什么"：

| 模板名 | 用途 | 何时选用 |
|--------|------|----------|
| `describe` | 通用全面描述 | 默认选项，不确定时用这个 |
| `describe-scene` | 场景/环境描述 | 风景、室内、街景等空间场景 |
| `describe-object` | 物体/产品描述 | 商品图、物品特写、产品照 |
| `describe-people` | 人物描述 | 人物肖像、群像、动作抓拍 |
| `describe-art` | 艺术风格描述 | 绘画、插画、设计稿、海报 |

**模板内容**：

- **describe**：请详细描述这张图片的内容，包括：主体、背景、色彩、文字、整体氛围。如实描述，不要遗漏重要细节。
- **describe-scene**：请描述这个场景：空间布局、光照条件、天气或时间线索、前景中景远景的层次、整体氛围。忽略无关细节。
- **describe-object**：请描述图中的主体物体：形状、材质、颜色、表面纹理、尺寸参照、品牌或标签信息。忽略背景。
- **describe-people**：请描述图中的人物：外貌特征、面部表情、肢体姿态、服装配饰、动作意图、情绪状态。
- **describe-art**：请从艺术角度分析这张图片：构图方式、色调搭配、风格流派、笔触或纹理、艺术手法、视觉冲击力。

### 任务型模板

回答"拿这张图干什么"：

| 模板名 | 用途 | 何时选用 |
|--------|------|----------|
| `ocr` | 文字提取 | 文档、截图、标牌、海报中的文字 |
| `layout` | 布局分析 | UI 截图、海报排版、网页结构 |
| `compare` | 对照检查 | 对照预期/规则检查图片是否符合 |
| `codegen` | 生成前端代码 | UI 截图还原为代码 |
| `troubleshoot` | 报错定位 | 报错弹窗、异常截图、日志图片 |

**模板内容**：

- **ocr**：请完整提取图片中的所有文字，保持原始排版格式。如果文字模糊或有歧义，标注[模糊]。不要遗漏任何文字。
- **layout**：请分析这张图片的布局结构：划分主要区域、标注各区域内容、描述元素排列方式和视觉层次。如果是 UI 截图，标注各组件位置。
- **compare**：请对照以下预期，逐项检查图片内容是否匹配。对每个检查项给出：符合/不符合/无法判断，并说明依据。
- **codegen**：请分析这张 UI 截图的结构，用文字描述如何用前端代码还原：1. 整体布局方案 2. 各区域组件 3. 关键样式属性 4. 交互逻辑。
- **troubleshoot**：这张图片显示了报错或异常信息。请：1. 提取所有错误文字 2. 判断错误类型 3. 分析可能原因 4. 给出修复建议。

### 自定义 Prompt

当预置模板不满足需求时，直接用 `--prompt` 传入任意文本：

```bash
python vl_vision.py food.jpg --prompt "判断这道菜是否烧焦了，给出你的信心百分比"
python vl_vision.py diagram.png --prompt "用 Mermaid 语法重新绘制这个流程图"
python vl_vision.py chart.png --prompt "读取图表数据，用 CSV 格式输出"
```

## Agent 自动调用指南

当你在 agent 工作流中遇到图片时，按以下流程操作：

### 判断是否需要调用

1. 当前 LLM 本身支持视觉 → 不需要调用，直接处理
2. 当前 LLM 不支持视觉 → 调用 vl-vision 获取图片描述
3. 不确定当前 LLM 是否支持视觉 → 尝试直接处理，如果失败则调用 vl-vision

### 选择模板

1. 用户明确要求分析方式 → 使用 `--prompt` 传入用户的要求
2. 用户没有指定 → 根据图片上下文判断：
   - 需要提取文字 → `ocr`
   - UI/设计相关 → `layout` 或 `codegen`
   - 报错/异常 → `troubleshoot`
   - 需要对照检查 → `compare`
   - 不确定 → `describe`（默认）

### 解读结果

- 成功时：`description` 字段包含 VL 模型的分析文本，直接作为"图片内容"使用
- 失败时：`error` 字段包含错误信息，告知用户并建议更换模型或检查 API Key

## 支持的图片格式

| 格式 | 扩展名 |
|------|--------|
| PNG | .png |
| JPEG | .jpg, .jpeg |
| WebP | .webp |
| GIF | .gif |

## 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VL_PROVIDER` | `siliconflow` | 默认 Provider |
| `VL_MODEL` | （由 Provider 决定） | 默认模型 |
| `SILICONFLOW_API_KEY` | — | 硅基流动 API Key（必须） |

### .env 文件

在项目根目录创建 `.env` 文件：

```
SILICONFLOW_API_KEY=sk-your-key-here
VL_PROVIDER=siliconflow
VL_MODEL=Qwen/Qwen2.5-VL-72B-Instruct
```

## 依赖

- Python >= 3.10
- requests

安装：
```bash
pip install requests
```

## 扩展新 Provider

在 `providers/` 目录下新建文件，继承 `VLProvider` 基类：

```python
from .base import VLProvider

class MyProvider(VLProvider):
    NAME = "my-provider"
    DEFAULT_MODEL = "my-model-v1"

    def analyze(self, image_path, prompt, model=None):
        # 实现调用逻辑
        ...
```

然后在 `providers/__init__.py` 的 `PROVIDERS` 字典中注册即可。
