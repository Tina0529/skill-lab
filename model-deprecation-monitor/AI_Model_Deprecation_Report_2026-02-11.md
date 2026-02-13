# AI 模型过期预警报告

**生成时间**: 2026-02-11
**数据来源**: deprecations.info + Anthropic / Google / OpenAI 官方文档
**关联 Issue**: [sparticleinc/felo-mygpt#1444](https://github.com/sparticleinc/felo-mygpt/issues/1444)

---

## 一、紧急告警（7天内停用或已停用）

### Anthropic Claude

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 | 状态 |
|---------|---------|---------|---------|------|
| `claude-3-5-sonnet-20240620` | 2025-10-28 | -107 天 | `claude-opus-4-6` | **已停用** |
| `claude-3-5-sonnet-20241022` | 2025-10-28 | -107 天 | `claude-opus-4-6` | **已停用** |
| `claude-3-opus-20240229` | 2026-01-05 | -38 天 | `claude-opus-4-6` | **已停用** |
| **`claude-3-7-sonnet-20250219`** | **2026-02-19** | **7 天** | `claude-opus-4-6` | **即将停用** |
| **`claude-3-5-haiku-20241022`** | **2026-02-19** | **7 天** | `claude-haiku-4-5-20251001` | **即将停用** |

### OpenAI

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 | 状态 |
|---------|---------|---------|---------|------|
| `codex-mini-latest` | 2026-01-16 | -27 天 | `gpt-5-codex-mini` | **已停用** |
| **`chatgpt-4o-latest`** | **2026-02-17** | **5 天** | `gpt-5.1-chat-latest` | **即将停用** |

---

## 二、警告（30天内停用）

### Azure OpenAI

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| `MAI-DS-R1` | 2026-02-27 | 15 天 | DeepSeek catalog models |

### AWS Bedrock

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| Claude 3.5 Sonnet v1 | 2026-03-01 | 17 天 | Claude Sonnet 4.5 |
| Claude 3.5 Sonnet v2 | 2026-03-01 | 17 天 | Claude Sonnet 4.5 |

### Google Gemini

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| `gemini-2.5-flash-preview-09-25` | 2026-02-17 | 5 天 | `gemini-3-flash-preview` |
| `imagen-4.0-generate-preview-06-06` | 2026-02-17 | 5 天 | `imagen-4.0-generate-001` |
| `imagen-4.0-ultra-generate-preview-06-06` | 2026-02-17 | 5 天 | `imagen-4.0-ultra-generate-001` |

---

## 三、提醒（60天内停用）

### Google Gemini

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| `gemini-2.0-flash` | 2026-03-31 | 47 天 | `gemini-2.5-flash` |
| `gemini-2.0-flash-001` | 2026-03-31 | 47 天 | `gemini-2.5-flash` |
| `gemini-2.0-flash-lite` | 2026-03-31 | 47 天 | `gemini-2.5-flash-lite` |
| `gemini-2.0-flash-lite-001` | 2026-03-31 | 47 天 | `gemini-2.5-flash-lite` |
| `gemini-embedding-001` | 2026-01-14 | 已停用 | `text-embedding-004` |

### OpenAI

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| `gpt-4o-realtime-preview` | 2026-03-24 | 40 天 | `gpt-realtime` |
| `gpt-4o-realtime-preview-2025-06-03` | 2026-03-24 | 40 天 | `gpt-realtime` |
| `gpt-4o-realtime-preview-2024-12-17` | 2026-03-24 | 40 天 | `gpt-realtime` |
| `gpt-4o-mini-realtime-preview` | 2026-03-24 | 40 天 | `gpt-realtime-mini` |
| `gpt-4o-audio-preview` | 2026-03-24 | 40 天 | `gpt-audio` |
| `gpt-4o-mini-audio-preview` | 2026-03-24 | 40 天 | `gpt-audio-mini` |

### AWS Bedrock

| 模型 ID | 停用日期 | 剩余天数 | 替代模型 |
|---------|---------|---------|---------|
| Claude 3.7 Sonnet | 2026-04-28 | 75 天 | Claude Sonnet 4.5 |

---

## 四、远期计划（60天以上）

### OpenAI

| 模型 ID | 停用日期 | 替代模型 |
|---------|---------|---------|
| `dall-e-2` | 2026-05-12 | `gpt-image-1`, `gpt-image-1-mini` |
| `dall-e-3` | 2026-05-12 | `gpt-image-1`, `gpt-image-1-mini` |
| `gpt-3.5-turbo-instruct` | 2026-09-28 | `gpt-5-mini`, `gpt-4.1-mini*` |
| `gpt-3.5-turbo-1106` | 2026-09-28 | `gpt-5-mini`, `gpt-4.1-mini*` |
| `babbage-002` | 2026-09-28 | `gpt-5-mini` |
| `davinci-002` | 2026-09-28 | `gpt-5-mini` |

### AWS Bedrock

| 模型 ID | 停用日期 | 替代模型 |
|---------|---------|---------|
| Claude Opus 4 | 2026-05-31 | Claude Opus 4.1 |
| Claude 3.5 Haiku | 2026-06-19 | Claude Haiku 4.5 |
| Titan Image Generator G1 v2 | 2026-06-30 | Nova Canvas, Nova 2 Omni |

### Azure OpenAI

| 模型 ID | 停用日期 | 替代模型 |
|---------|---------|---------|
| `Cohere-rerank-v3.5` | 2026-05-14 | `Cohere-rerank-v4.0-pro/fast` |

### Google Gemini

| 模型 ID | 停用日期 | 替代模型 |
|---------|---------|---------|
| `gemini-2.5-pro` | 2026-06-17 | `gemini-3-pro-preview` |
| `gemini-2.5-flash` | 2026-06-17 | `gemini-3-flash-preview` |
| `gemini-2.5-flash-image` | 2026-10-02 | - |
| `gemini-2.5-flash-lite` | 2026-07-22 | - |
| `text-embedding-001` | 2026-07-14 | `text-embedding-004` |
| `imagen-4.0-*` 系列 | 2026-06-24 | `gemini-3-pro-image-preview` |

---

## 五、安全模型一览（Active 状态，暂无停用计划）

### Anthropic Claude

| 模型 ID | 最早停用日期 |
|---------|------------|
| `claude-opus-4-6` | 不早于 2027-02-05 |
| `claude-opus-4-5-20251101` | 不早于 2026-11-24 |
| `claude-opus-4-1-20250805` | 不早于 2026-08-05 |
| `claude-opus-4-20250514` | 不早于 2026-05-14 |
| `claude-sonnet-4-5-20250929` | 不早于 2026-09-29 |
| `claude-sonnet-4-20250514` | 不早于 2026-05-14 |
| `claude-haiku-4-5-20251001` | 不早于 2026-10-15 |

### Google Gemini

| 模型 ID | 状态 |
|---------|------|
| `gemini-3-pro-preview` | Active（无停用日期） |
| `gemini-3-pro-image-preview` | Active（无停用日期） |
| `gemini-3-flash-preview` | Active（无停用日期） |

---

## 六、针对 felo-mygpt 项目的操作建议

> 参考 Issue #1444 中列出的项目使用模型

### 立即操作（本周内）

1. **`claude-3-5-sonnet-20241022`** - 已停用 107 天
   - 替换为 `claude-sonnet-4-5-20250929` 或 `claude-opus-4-6`
   - 配置位置：`mygpt/config/models.py`

2. **`claude-3-7-sonnet-20250219`** - 7天后停用（2/19）
   - 替换为 `claude-opus-4-6`
   - 如有使用请尽快迁移

3. **`claude-3-5-haiku-20241022`** - 7天后停用（2/19）
   - 替换为 `claude-haiku-4-5-20251001`

4. **`chatgpt-4o-latest`** - 5天后停用（2/17）
   - 替换为 `gpt-5.1-chat-latest`

### 本月内

5. **AWS Bedrock Claude 3.5 Sonnet v1/v2** - 17天后停用（3/1）
   - 迁移到 Claude Sonnet 4.5

6. **`gemini-2.0-flash`** - 47天后停用（3/31）
   - 迁移到 `gemini-2.5-flash`
   - 配置位置：`mygpt/rag/summarizer.py`

7. **`gpt-4o-realtime/audio`** 系列 - 40天后停用（3/24）
   - 迁移到 `gpt-realtime` / `gpt-audio`

### 持续关注

8. 建议配置 **GitHub Actions** 每日自动检查模型过期信息
9. 维护 `models_in_use.json` 模型清单，每次上线新模型时更新
10. AWS Bedrock 用户关注 `modelLifecycle.status` 从 ACTIVE 变为 LEGACY 的模型

---

## 七、数据来源

| 来源 | URL |
|------|-----|
| deprecations.info | https://deprecations.info/v1/feed.json |
| OpenAI Deprecations | https://platform.openai.com/docs/deprecations |
| Anthropic Model Deprecations | https://docs.anthropic.com/en/docs/about-claude/model-deprecations |
| Google Gemini Deprecations | https://ai.google.dev/gemini-api/docs/deprecations |
| AWS Bedrock Model Lifecycle | https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html |
| Azure OpenAI Retirements | https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-retirements |

---

## 八、统计摘要

- **总过期条目数**: 148 条（来自 deprecations.info）
- **覆盖厂商**: OpenAI, Anthropic, Google, AWS Bedrock, Azure, Cohere, Google Vertex
- **紧急告警 (7天内)**: 4 个模型
- **警告 (30天内)**: 5 个模型
- **提醒 (60天内)**: 11 个模型
