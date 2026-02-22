---
name: ai-video-maker
description: AI生成科普/教程视频的完整方法论和自动化工具链。从文案到TTS配音到AI图片生成到ffmpeg合成，全流程自动化。适用于任何主题的PPT风格科普视频制作。当用户要求制作视频、生成视频素材、或复刻视频制作流程时激活。
---

# AI Video Maker — PPT科普视频全流程

零人工素材、零剪辑软件，纯AI+代码生成完整视频。

## Quick Start

```bash
# 1. 安装依赖
pip install -r scripts/requirements.txt

# 2. 设置 API Key
export GEMINI_API_KEY="your-key-here"

# 3a. 从主题一键生成（AI 自动写文案 + 生成视频）
python3 scripts/pipeline.py --generate-script "AI发展简史" --config my-video/project.yaml

# 3b. 或者手动编辑配置
mkdir my-video && cp scripts/project_template.yaml my-video/project.yaml
# 编辑 project.yaml，填入 pages 内容

# 4. 一键生成
python3 scripts/pipeline.py --config my-video/project.yaml
```

**也可以分步运行**：

```bash
# 只生成 TTS
python3 scripts/pipeline.py --config project.yaml --steps tts

# 只生成图片
python3 scripts/pipeline.py --config project.yaml --steps images

# 只合成视频（需要 audio/ 和 images/ 已准备好）
python3 scripts/pipeline.py --config project.yaml --steps subtitles segments merge

# 只处理特定页
python3 scripts/pipeline.py --config project.yaml --steps tts --pages 3 5 8

# 使用分辨率预设（竖屏短视频）
python3 scripts/pipeline.py --config project.yaml --preset shorts

# 断点续传（上次中断后自动从断点继续）
python3 scripts/pipeline.py --config project.yaml
# 强制重跑（忽略之前的进度）
python3 scripts/pipeline.py --config project.yaml --no-resume

# 只运行质量校验
python3 scripts/pipeline.py --config project.yaml --validate-only
```

---

## 概述

**输入**：一个 YAML 配置文件（含文案、字幕、图片 prompt）
**输出**：带字幕、配音、Ken Burns 动画、转场效果的完整视频（MP4）

### 流程

```
Step 0: 文案生成 (script_generator.py, 可选)   → project.yaml
  ↓
project.yaml (配置)
  ↓
Step 1: TTS 配音 (tts_service.py)              → audio/page_XX.wav
  ↓
Step 2: AI 生成配图 (image_service.py)          → images/page_XX.png
  ↓
Step 3: 字幕处理 (subtitle_service.py)
  ├── static 模式: 烧字幕到图片                → images_sub/page_XX.png
  └── dynamic 模式: 生成 ASS 字幕文件           → subtitles/page_XX.ass
  ↓
Step 4: ffmpeg 合成 (video_service.py)          → video/final_subtitled.mp4
  ↓
Step 5: BGM 混音 (bgm_service.py, 可选)        → video/final_with_bgm.mp4
  ↓
Step 6: 质量校验 (validator.py, 自动)           → validation_report.json
  ↓
Step 7: 封面生成 (Gemini Image API)            → images/cover.png + images/cover_4x3.png
```

### 模块结构

```
scripts/
├── pipeline.py             # 主入口，串联所有步骤
├── config.py               # YAML 配置加载与验证
├── tts_service.py          # TTS: Gemini / Edge-TTS
├── image_service.py        # 图片: Gemini / Pillow Fallback
├── subtitle_service.py     # 字幕: static(boxed/outlined) / dynamic(ASS)
├── alignment_service.py    # WhisperX 强制对齐 → 逐词时间戳
├── video_service.py        # ffmpeg: Ken Burns + xfade + ASS + 合并
├── bgm_service.py          # BGM: 循环/裁剪 + amix 混音
├── resolution_presets.py   # 多分辨率预设 + 图片适配策略
├── script_generator.py     # LLM 文案生成：主题 → project.yaml
├── checkpoint.py           # 断点续传：JSON 状态持久化
├── retry.py                # 指数退避重试 + 错误分类
├── validator.py            # 质量校验：音频/图片/视频检查
├── project_template.yaml   # 配置模板
└── requirements.txt        # Python 依赖
```

---

## 配置文件 (project.yaml)

所有参数集中在一个 YAML 文件中，详细模板见 `scripts/project_template.yaml`。

### pages 数组

每页 = 一段配音 + 一条字幕 + 一个图片 prompt：

```yaml
pages:
  - page: 1
    narration: |
      大家好，欢迎来到我们的频道。今天给大家介绍...
    subtitle: "大家好\n欢迎来到我们的频道"
    image_prompt: >
      A welcoming modern tech illustration, 1920x1080 landscape.
      Large Chinese title text "欢迎" prominently placed at center.
      Clean blue gradient background. Professional atmosphere.
```

### TTS 配置

```yaml
tts:
  provider: gemini    # gemini | edge
  voice: Leda         # 见下方声音列表
  speed: 1.0          # 语速倍率
```

**Gemini 可用声音**：Leda(知性女声) / Kore(明亮女声) / Aoede(温暖女声) / Puck(活泼男声) / Charon(沉稳男声) / Zephyr(中性)

### 图片配置

```yaml
image_gen:
  provider: gemini
  model: gemini-3-pro-image-preview
  style_prompt: "Professional flat illustration, blue tech aesthetic"
```

### 字幕配置

```yaml
subtitle:
  mode: static        # static (烧到图片) | dynamic (ASS 逐词高亮)
  style: boxed        # boxed (半透明黑底框) | outlined (白字黑描边) — 仅 static 模式
  font_size: 36
  karaoke: true       # 逐词变色高亮 — 仅 dynamic 模式
  language: zh        # 对齐语言 — 仅 dynamic 模式
```

**Dynamic 模式** 使用 WhisperX 强制对齐，生成带 `\k` 标签的 ASS 字幕，实现逐词高亮效果。需额外安装 `pip install whisperx pysubs2`。未安装时自动降级为均匀时间分割。

### BGM 配置

```yaml
bgm:
  enabled: true       # 是否启用背景音乐
  file: bgm/music.mp3 # BGM 文件路径
  volume: 0.15        # BGM 音量（0.0-1.0，0.15 为轻柔背景）
  fade_in: 2.0        # 淡入时长（秒）
  fade_out: 3.0       # 淡出时长（秒）
```

BGM 自动循环/裁剪到视频长度，用 amix 混合配音和 BGM。

### 文案生成 (Step 0)

无需手写文案，给一个主题即可自动生成完整 project.yaml：

```bash
# 生成 10 页文案（默认）
python3 scripts/pipeline.py --generate-script "AI发展简史" --config my-video/project.yaml

# 指定页数
python3 scripts/pipeline.py --generate-script "量子计算入门" --config my-video/project.yaml --num-pages 8

# 生成后直接运行（不需要额外命令）
python3 scripts/pipeline.py --generate-script "区块链原理" --config my-video/project.yaml
python3 scripts/pipeline.py --config my-video/project.yaml
```

生成的每页包含 narration（配音文案）、subtitle（精简字幕）、image_prompt（英文图片描述）。建议生成后检查 YAML 文件，微调不满意的部分再运行 pipeline。

### 断点续传

Pipeline 自动保存每页每步的完成状态到 `{project_dir}/.pipeline_state.json`。

- **自动恢复**：再次运行同一配置时，自动跳过已完成的步骤
- **强制重跑**：`--no-resume` 忽略之前的进度，全部重新生成
- **典型场景**：API 限流导致第 5 页图片失败 → 重新运行 → 自动从第 5 页继续

```bash
# 运行到一半 Ctrl+C 中断
python3 scripts/pipeline.py --config project.yaml
# ^C

# 再次运行，自动从断点继续
python3 scripts/pipeline.py --config project.yaml

# 强制全部重跑
python3 scripts/pipeline.py --config project.yaml --no-resume
```

### 质量校验

Pipeline 完成后自动运行质量校验，也可单独运行：

```bash
python3 scripts/pipeline.py --config project.yaml --validate-only
```

校验内容：
- **音频**：文件存在性、大小、静音检测、时长范围（5-60s）
- **图片**：文件存在性、大小（>200KB = 真实 AI 图片）
- **最终视频**：文件存在性、大小、时长合理性

结果输出为 `validation_report.json`，每项标记 pass / warning / error + 严重程度。

### 视频配置

```yaml
video:
  width: 1920
  height: 1080
  resolution_preset: ""    # youtube | shorts | instagram | xiaohongshu | bilibili
  adapt_strategy: ""       # crop_center | letterbox | blur_fill
  kb_scale: 1.08           # Ken Burns 缩放比例
  transition_dur: 0.8      # 转场时长
```

### 分辨率预设

| 预设 | 尺寸 | 比例 | 默认适配策略 | 适用平台 |
|------|------|------|-------------|---------|
| youtube | 1920x1080 | 16:9 | crop_center | YouTube |
| shorts | 1080x1920 | 9:16 | blur_fill | YouTube Shorts / TikTok |
| instagram | 1080x1080 | 1:1 | crop_center | Instagram |
| xiaohongshu | 1080x1440 | 3:4 | blur_fill | 小红书 / Pinterest |
| bilibili | 1920x1080 | 16:9 | crop_center | Bilibili |

**图片适配策略**：
- **crop_center**：放大填满后居中裁剪（适合同方向图片）
- **letterbox**：缩放到框内，黑边填充（保留完整画面）
- **blur_fill**：模糊放大版做背景 + 原图居中（无黑边，适合竖屏）

使用 CLI 快速切换：`python3 scripts/pipeline.py --config project.yaml --preset shorts`

---

## 文案写作要点

- **每页配音** 15-35 秒（太长会闷，太短切换太快）
- **总时长** 3-8 分钟为佳
- **8-12 页**
- 开头要有 **hook**（痛点/问题/反差）
- 中间有对比/场景/案例
- 结尾有 **CTA**（关注/点赞/预告）
- **字幕** 是配音的精简版，每页 2-3 行，每行 ≤20 字

## 图片 Prompt 要点

1. **用英文写 prompt**（AI 英文理解力更强）
2. **详细描述画面**（每个 prompt ≥80 词）
3. **明确指定图中文字**（中文标题写进 prompt）
4. **指定尺寸**：如 1920x1080 landscape
5. **统一全片视觉风格**（通过 `style_prompt` 全局设定）

**Prompt 模板**：

```
A [STYLE] illustration, 1920x1080. [SCENE DESCRIPTION with specific visual elements].
Large Chinese title text "[中文标题]" prominently placed at [position].
[Additional text/labels]. [Color scheme]. [Mood/atmosphere].
```

---

## 封面生成（Step 7 - 视频完成后必须执行）

视频生成完成后，**必须生成两种比例的封面图**：

### 两种封面格式

| 格式 | 尺寸 | 比例 | 用途 | 输出路径 |
|------|------|------|------|---------|
| 16:9 | 1920x1080 | 16:9 | 视频播放页封面 | `images/cover.png` |
| 4:3 | 1440x1080 或 1200x900 | 4:3 | B站首页推荐缩略图 | `images/cover_4x3.png` |

> **B站首页推荐流使用 4:3 封面**，如果只有 16:9 会被自动裁切导致关键信息丢失。

### 生成方式

使用 Gemini Image API（与 image_service.py 相同的 `generate_content` + `response_modalities=["IMAGE", "TEXT"]` 方式）：

```python
from google import genai
client = genai.Client()
# 16:9 封面
response_16x9 = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Generate a 1920x1080 cover image. [封面描述 prompt]",
    config={"response_modalities": ["IMAGE", "TEXT"]},
)
# 4:3 封面
response_4x3 = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Generate a 1200x900 (4:3 aspect ratio) cover image. [封面描述 prompt]",
    config={"response_modalities": ["IMAGE", "TEXT"]},
)
```

### 封面 Prompt 要点

- 封面要**吸引眼球**：高对比度、大标题文字、视觉冲击力
- 包含视频核心主题的**中文标题**（简短版，不是完整视频标题）
- 与视频内页保持**统一视觉风格**（配色、字体风格）
- 4:3 版本注意**构图居中**，因为尺寸更窄，边缘内容要收紧
- **不使用 emoji 图标**，用线性图标或纯文字排版

### 封面 Prompt 模板

```
Create an eye-catching video cover image, [尺寸].
[视觉风格描述，与视频内页一致].
Large bold Chinese title "[标题关键词]" prominently displayed.
[核心视觉元素]. High contrast, clean layout.
No emoji icons. Professional and modern.
```

---

## 技术细节

### Ken Burns 效果

使用 `scale+crop` 方案（**不要用 zoompan**，会导致画面抖动）。4 种运动模式循环：静态居中 → 左上到右下 → 静态居中 → 右下到左上。

### xfade 转场

5 种转场效果循环：fade → fadeblack → slideleft → dissolve → fadewhite。
当 xfade 失败时自动降级为简单 concat。

### 动态字幕 (ASS Karaoke)

WhisperX 强制对齐 → 逐词时间戳 → ASS `\k` 标签 → ffmpeg ass filter 叠加。无 WhisperX 时自动降级为均匀时间分割。

### BGM 混音

ffmpeg amix filter，配音音量 1.0 / BGM 音量可配置（默认 0.15）。BGM 自动循环/裁剪到视频长度，片头淡入、片尾淡出。

### 指数退避重试

所有 API 调用使用 `@exponential_backoff` 装饰器：`delay = min(base * 2^attempt + jitter, max_delay)`。区分 RetryableError（限流、网络超时，会重试）和 PermanentError（无效 API Key、格式错误，立即失败）。默认最多重试 3 次。

### 音频验证

生成后自动验证音频振幅（Gemini TTS 偶尔返回静音），失败自动重试最多 3 次。

### 图片验证

AI 生成的真实图片通常 >200KB，Pillow fallback 生成的占位图 <120KB。当 AI 生成失败时自动降级为 Pillow 占位图。

### 断点续传实现

每完成一页的某个步骤就写入 `.pipeline_state.json`，格式为 `{page_num: {step_name: {completed, timestamp, error}}}`。恢复时逐页逐步检查，跳过已完成的项。

---

## 常见坑

| 问题 | 原因 | 解决 |
|------|------|------|
| Ken Burns 画面抖动 | 用了 zoompan | 改用 scale+crop |
| 字幕不显示 | ffmpeg 缺 drawtext | 用 Pillow 预烧字幕（static 模式） |
| 后半段音频无声 | TTS API 返回空数据 | pipeline 自动验证振幅+重试 |
| 图片质量差 | 用了错误模型/fallback | 检查文件大小 >200KB |
| 图片底部被裁 | Ken Burns 放大+字幕占位 | 用 outlined 样式 + image_shrink: 0.92 |
| 语速太慢 | Gemini TTS 默认偏慢 | 设置 tts.speed: 1.1 |
| 转场闪烁 | xfade offset 计算错误 | pipeline 已内置正确公式 |
| 动态字幕不工作 | 缺少 whisperx | `pip install whisperx` 或改用 static 模式 |
| 竖屏黑边 | 图片比例不匹配 | 使用 blur_fill 适配策略 |
| API 限流中断 | 连续调用太多 | 自动断点续传，重新运行即可继续 |
| 文案生成格式错误 | LLM 返回非标准 JSON | 自动清理 markdown 代码块标记 |
| 重复生成浪费 API | 没有断点机制 | 默认启用 checkpoint，跳过已完成步骤 |

---

## 字体路径参考

| 系统 | 中文字体路径 |
|------|------------|
| macOS 中文 | `/System/Library/Fonts/STHeiti Medium.ttc` |
| macOS 日文 | `/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc` |
| Linux | `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc` |
| Windows | `C:\Windows\Fonts\msyh.ttc` |

## 依赖

```bash
pip install -r scripts/requirements.txt
# 核心：google-genai, Pillow, PyYAML
# 可选：edge-tts (免费 TTS 替代方案)
# 可选：whisperx, pysubs2 (动态字幕)

# 系统依赖
brew install ffmpeg  # 或 apt install ffmpeg
```

## 适用场景

- AI 科普视频（技术解说）
- 产品介绍视频
- 教程系列
- 新闻/资讯播报
- YouTube Shorts / TikTok 竖屏短视频
- 任何"图片+配音"风格的视频

不适用于：实拍视频、Vlog、动画片

## CLI 参数速查

| 参数 | 用途 | 示例 |
|------|------|------|
| `--config PATH` | 指定配置文件（必需） | `--config my-video/project.yaml` |
| `--steps STEP...` | 只运行指定步骤 | `--steps tts images` |
| `--pages NUM...` | 只处理指定页 | `--pages 3 5 8` |
| `--preset NAME` | 使用分辨率预设 | `--preset shorts` |
| `--generate-script TOPIC` | AI 生成文案 | `--generate-script "AI发展简史"` |
| `--num-pages N` | 文案生成页数（默认 10） | `--num-pages 8` |
| `--validate-only` | 只运行质量校验 | `--validate-only` |
| `--no-resume` | 忽略断点，强制重跑 | `--no-resume` |

## 项目输出目录

```
my-video-project/
├── project.yaml              # 配置文件
├── .pipeline_state.json      # 断点续传状态（自动管理）
├── audio/                    # TTS 音频（自动生成）
│   ├── page_01.wav
│   └── ...
├── images/                   # AI 图片（自动生成）
│   ├── page_01.png
│   ├── ...
│   ├── cover.png             # 16:9 封面（1920x1080）
│   └── cover_4x3.png         # 4:3 封面（B站首页推荐用）
├── images_sub/               # 带字幕的图片（自动生成，static 模式）
├── subtitles/                # ASS 字幕文件（自动生成，dynamic 模式）
├── segments/                 # 单页视频片段（自动生成）
├── video/
│   ├── final_subtitled.mp4   # 最终视频
│   └── final_with_bgm.mp4   # 带 BGM 的版本（可选）
└── validation_report.json    # 质量校验报告（自动生成）
```
