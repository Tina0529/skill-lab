# AI Video Maker

AI 全自动视频制作流水线。从 YAML 配置文件到成品视频，一条命令搞定 TTS 配音、AI 画面、字幕烧录、视频合成。

## 功能特点

- **全流程自动化**：文案 → TTS 配音 → AI 图片 → 字幕 → Ken Burns 动效 → 转场合成，一条命令完成
- **YAML 驱动**：所有内容和参数集中在一个配置文件，改配置即可出片
- **多 TTS 引擎**：Gemini TTS（高质量） / Edge-TTS（免费替代）
- **AI 图片生成**：Gemini API 生成配图，全局 style_prompt 统一视觉风格
- **两种字幕模式**：静态描边字幕（Pillow 烧录） / 动态逐词高亮字幕（WhisperX + ASS）
- **BGM 混音**：自动循环/裁剪 + 淡入淡出
- **多分辨率预设**：横版(YouTube) / 竖版(Shorts/TikTok) / 方形(Instagram) / 小红书
- **断点续传**：API 失败后重新运行自动从断点继续
- **质量校验**：22 项自动检查，确保产出完整可用
- **LLM 文案生成**：给一个主题，AI 自动生成完整文案和图片 prompt

## 快速开始

### 1. 安装依赖

```bash
pip install google-genai Pillow PyYAML

# 系统依赖
brew install ffmpeg  # macOS
# apt install ffmpeg  # Linux
```

### 2. 设置 API Key

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 3. 准备配置文件

```bash
# 复制模板
mkdir my-video
cp scripts/project_template.yaml my-video/project.yaml
# 编辑 project.yaml，填入 pages 内容
```

或者让 AI 自动生成文案：

```bash
python3 scripts/pipeline.py --generate-script "AI发展简史" --config my-video/project.yaml
```

### 4. 一键生成视频

```bash
python3 scripts/pipeline.py --config my-video/project.yaml
```

约 15 分钟后，成品视频在 `my-video/video/final_subtitled.mp4`。

## 分步执行

```bash
# 只生成 TTS 配音
python3 scripts/pipeline.py --config project.yaml --steps tts

# 只生成 AI 图片
python3 scripts/pipeline.py --config project.yaml --steps images

# 只合成视频（需要 audio/ 和 images/ 已准备好）
python3 scripts/pipeline.py --config project.yaml --steps subtitles segments merge

# 只处理特定页
python3 scripts/pipeline.py --config project.yaml --steps tts --pages 3 5 8

# 竖屏短视频
python3 scripts/pipeline.py --config project.yaml --preset shorts

# 质量校验
python3 scripts/pipeline.py --config project.yaml --validate-only
```

## 配置文件 (project.yaml)

```yaml
project_dir: /path/to/my-video

tts:
  provider: gemini         # gemini | edge
  voice: Leda              # Leda(知性女声) / Kore(明亮女声) / Puck(活泼男声) / Charon(沉稳男声)
  speed: 1.1               # 语速倍率

image_gen:
  provider: gemini
  model: gemini-3-pro-image-preview
  style_prompt: >
    Professional flat illustration, modern tech aesthetic,
    clean composition, vibrant colors.

subtitle:
  mode: static             # static(烧到图片) | dynamic(ASS逐词高亮)
  style: outlined          # outlined(白字黑描边) | boxed(半透明黑底)
  font_size: 28

video:
  width: 1920
  height: 1080
  kb_scale: 1.05           # Ken Burns 缩放比例
  transition_dur: 0.8      # 转场时长(秒)
  crf: 18                  # 视频质量(越低越好)

bgm:
  enabled: false            # 是否启用背景音乐
  file: bgm/music.mp3
  volume: 0.15

pages:
  - page: 1
    narration: |
      大家好，欢迎来到我们的频道...
    subtitle: "大家好\n欢迎来到我们的频道"
    image_prompt: >
      A welcoming modern tech illustration, 1920x1080 landscape.
      Large Chinese title text prominently placed at center.
```

每页 = 一段配音文案 + 精简字幕 + 英文图片 prompt。建议每页 15-35 秒配音，全片 8-12 页。

## 分辨率预设

| 预设 | 尺寸 | 适用平台 |
|------|------|---------|
| youtube | 1920x1080 | YouTube / B站 |
| shorts | 1080x1920 | YouTube Shorts / TikTok / 抖音 |
| instagram | 1080x1080 | Instagram |
| xiaohongshu | 1080x1440 | 小红书 / Pinterest |

## 输出目录

```
my-video/
├── project.yaml              # 配置文件
├── audio/                    # TTS 音频
├── images/                   # AI 生成的图片
├── images_sub/               # 带字幕的图片（static 模式）
├── segments/                 # 单页视频片段
├── video/
│   └── final_subtitled.mp4   # 最终成品
└── validation_report.json    # 质量校验报告
```

## 项目结构

```
ai-video-maker/
├── SKILL.md                    # Claude Code Skill 定义
├── README.md                   # 本文档
└── scripts/
    ├── pipeline.py             # 主入口，串联所有步骤
    ├── config.py               # YAML 配置加载
    ├── tts_service.py          # TTS 语音合成
    ├── image_service.py        # AI 图片生成
    ├── subtitle_service.py     # 字幕处理
    ├── video_service.py        # FFmpeg 视频合成
    ├── alignment_service.py    # WhisperX 逐词对齐（动态字幕）
    ├── bgm_service.py          # BGM 混音
    ├── resolution_presets.py   # 多分辨率预设
    ├── script_generator.py     # LLM 文案自动生成
    ├── checkpoint.py           # 断点续传
    ├── retry.py                # 指数退避重试
    ├── validator.py            # 质量校验
    ├── project_template.yaml   # 配置模板
    └── requirements.txt        # Python 依赖
```

## CLI 参数速查

| 参数 | 用途 | 示例 |
|------|------|------|
| `--config PATH` | 指定配置文件 | `--config my-video/project.yaml` |
| `--steps STEP...` | 只运行指定步骤 | `--steps tts images` |
| `--pages NUM...` | 只处理指定页 | `--pages 3 5 8` |
| `--preset NAME` | 分辨率预设 | `--preset shorts` |
| `--generate-script TOPIC` | AI 生成文案 | `--generate-script "量子计算"` |
| `--num-pages N` | 文案生成页数 | `--num-pages 8` |
| `--validate-only` | 只运行质量校验 | |
| `--no-resume` | 忽略断点，强制重跑 | |

## 批量生产技巧

制作多个视频时，使用交错并行策略最大化效率：

```
视频A: [TTS] → [图片生成] → [合成]
视频B:          [TTS]      → [图片生成] → [合成]
视频C:                       [TTS]      → [图片生成] → [合成]
```

- 图片生成是瓶颈（每个视频约 8 分钟），合成步骤纯本地
- 建议同时最多 1 个图片生成 + 1 个 TTS + 1 个合成
- 单个 API Key 建议每天不超过 15 个视频

## 实测数据

- 14 个教程视频（每个 10 页 / 4 分钟），全部自动生成
- 单个视频约 40MB，22 项质量检查全部通过
- 单个视频 API 成本约 $0.5（约 3.5 元）

## 适用场景

- 教程 / 科普类视频批量制作
- 产品介绍视频
- 系列课程自动生产
- YouTube Shorts / TikTok 竖屏短视频
- 任何"图片 + 配音"风格的视频

不适用于：实拍视频、Vlog、动画片

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| GEMINI_API_KEY not set | 在命令前加 `export GEMINI_API_KEY="your-key"` |
| 图片生成超时 | 内置重试机制，一般第二次成功 |
| xfade 合并失败 | 自动降级为 concat 拼接 |
| 字幕显示不全 | 每行不超过 20 个中文字符，用 `\n` 换行 |
| API 限流中断 | 自动断点续传，重新运行即可继续 |
| 动态字幕不工作 | `pip install whisperx pysubs2` 或改用 static 模式 |

## 技术栈

- Python 3.10+
- [Google Gemini API](https://ai.google.dev/)（TTS + 图片生成）
- [Pillow](https://pillow.readthedocs.io/)（字幕烧录）
- [FFmpeg](https://ffmpeg.org/) 5.0+（视频合成）
- [WhisperX](https://github.com/m-bain/whisperX)（动态字幕，可选）

## License

MIT
