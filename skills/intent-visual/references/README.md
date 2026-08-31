# intent-visual 参考文件目录

本目录存放从 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md)（MIT 许可，版权归 VoltAgent 及各文件作者所有）vendor 进来的常备风格参考。用途和取用规则见 `../SKILL.md` 的「参考文件取用」节。

## 定版信息

- **来源仓库**：https://github.com/VoltAgent/awesome-design-md
- **pin commit**：`8147538b4226ae41e2487a9179e3bcc1f68e8554`（上游 2026-07-31 提交）
- **许可**：MIT（https://github.com/VoltAgent/awesome-design-md/blob/main/LICENSE）
- **文件保持上游原样，不做任何改写**。上游更新后由维护流程统一升级 pin 并重新核对，不在运行中静默拉新。

## 常备参考（按风格方向选取）

| 文件 | 来源路径 | 代表方向 | 风格轴 |
|---|---|---|---|
| [vercel.md](vercel.md) | design-md/vercel/DESIGN.md | 极简工具感 | 无彩黑白、高信息密度、无装饰 |
| [notion.md](notion.md) | design-md/notion/DESIGN.md | 柔和产品感 | 浅色卡片、中圆角、低密度 |
| [stripe.md](stripe.md) | design-md/stripe/DESIGN.md | 品牌渐变感 | 有彩色主张、渐变、营销页气质 |
| [apple.md](apple.md) | design-md/apple/DESIGN.md | 内容大图感 | 大字排版、大图、留白讲故事 |

这四份兼任两个角色：

1. **B 分支（方向样张）的弹药库**——用户说不清想要什么风格时，intent-visual 从这四份各抽值渲染候选样张，让用户看图选；
2. **格式样板**——任何生成场景先看一份，校准"只写值、不写形容词"的粒度。

## 运行时按需取用（未 vendored 的品牌）

参考文件不整体镜像进仓库：运行时按用户指名的品牌，用下面的 URL 模式取那一份（pin commit 不可省）：

```text
https://raw.githubusercontent.com/VoltAgent/awesome-design-md/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/{品牌目录}/DESIGN.md
```

品牌目录名以下方索引为准。取回的文件只进上下文，不落盘；`visual-design.md` 的「来源与替代」节记录 URL + commit + 日期。

## 品牌目录索引（pin commit 时点，共 74 个）

airbnb airtable apple binance bmw bmw-m bugatti cal claude clay clickhouse cohere coinbase composio cursor dell-1996 elevenlabs expo ferrari figma framer hashicorp hp ibm intercom kraken lamborghini linear.app lovable mastercard meta minimax mintlify miro mistral.ai mongodb nike nintendo-2001 notion nvidia ollama opencode.ai pinterest playstation posthog raycast renault replicate resend revolut runwayml sanity sentry shopify slack spacex spotify starbucks stripe supabase superhuman tesla theverge together.ai uber vercel vodafone voltagent warp webflow wired wise x.ai zapier

> 注意：`linear.app`、`mistral.ai`、`x.ai` 等目录名带域名后缀，拼 URL 时照原样使用。各品牌的一句话风格描述可按需取上游 README（同一 pin commit）查看。
