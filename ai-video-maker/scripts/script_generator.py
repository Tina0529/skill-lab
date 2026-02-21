#!/usr/bin/env python3
"""LLM-powered script generator — topic → structured YAML config.

Generates narration, subtitle, and image_prompt for each page
using Gemini, then writes a complete project.yaml.
"""

import json
import os
import re

import yaml


SCRIPT_PROMPT = """你是一位专业的科普视频文案策划师。请根据主题生成一个完整的视频文案。

## 主题
{topic}

## 要求
- 生成 {num_pages} 页内容
- 每页包含：narration（配音文案）、subtitle（字幕）、image_prompt（图片提示词）
- narration：口语化，15-35 秒可朗读完的文字量
- subtitle：narration 的精简版，2-3 行，每行不超过 20 个字，用 \\n 分行
- image_prompt：用英文写，详细描述画面（至少 80 词），指定 1920x1080 landscape，包含中文标题文字
- 第 1 页是开头（hook，引起兴趣）
- 中间页是正文（案例、对比、解说）
- 最后 1 页是结尾（总结 + CTA）
- 全片保持统一的视觉风格

## 输出格式
请严格按照以下 JSON 格式输出（不要添加 markdown 代码块标记）：

[
  {{
    "page": 1,
    "narration": "配音文字...",
    "subtitle": "字幕第一行\\n字幕第二行",
    "image_prompt": "English image description..."
  }},
  ...
]"""


def generate_script(topic: str, num_pages: int = 10,
                    api_key_env: str = "GEMINI_API_KEY",
                    model: str = "gemini-2.5-flash-preview-04-17") -> list[dict]:
    """Generate video script using Gemini.

    Args:
        topic: Video topic
        num_pages: Number of pages to generate (8-12 recommended)
        api_key_env: Environment variable name for API key
        model: Gemini model to use

    Returns:
        List of page dicts with narration, subtitle, image_prompt
    """
    from google import genai

    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ValueError(f"API key not found in environment variable: {api_key_env}")

    client = genai.Client(api_key=api_key)

    prompt = SCRIPT_PROMPT.format(topic=topic, num_pages=num_pages)

    print(f"  Generating {num_pages}-page script for: {topic}")
    print(f"  Model: {model}")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    # Parse JSON from response
    text = response.text.strip()

    # Remove markdown code block if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    pages = json.loads(text)

    if not isinstance(pages, list):
        raise ValueError("Expected JSON array of pages")

    print(f"  Generated {len(pages)} pages")
    return pages


def write_project_yaml(pages: list[dict], output_path: str,
                       topic: str = "",
                       style_prompt: str = "",
                       tts_voice: str = "Leda") -> None:
    """Write generated script to a complete project YAML config.

    Args:
        pages: List of page dicts from generate_script()
        output_path: Path to write YAML file
        topic: Original topic (for comment)
        style_prompt: Global image style prompt
        tts_voice: TTS voice to use
    """
    project_dir = os.path.dirname(output_path) or "."

    config = {
        "project_dir": project_dir,
        "tts": {
            "provider": "gemini",
            "voice": tts_voice,
            "speed": 1.0,
        },
        "image_gen": {
            "provider": "gemini",
            "model": "gemini-3-pro-image-preview",
            "style_prompt": style_prompt,
        },
        "subtitle": {
            "mode": "static",
            "style": "boxed",
            "font_size": 36,
        },
        "video": {
            "width": 1920,
            "height": 1080,
        },
        "pages": [],
    }

    for p in pages:
        page_config = {
            "page": p.get("page", 0),
            "narration": p.get("narration", "").strip() + "\n",
            "subtitle": p.get("subtitle", ""),
            "image_prompt": p.get("image_prompt", "").strip() + "\n",
        }
        config["pages"].append(page_config)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Write with comment header
    header = f"# AI Video Maker — Auto-generated script\n# Topic: {topic}\n\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"  Config saved: {output_path}")
    print(f"  Pages: {len(pages)}")


def generate_and_save(topic: str, output_path: str,
                      num_pages: int = 10,
                      style_prompt: str = "",
                      tts_voice: str = "Leda") -> str:
    """One-shot: generate script and save as project.yaml.

    Returns the output path.
    """
    print("\n" + "=" * 60)
    print("[SCRIPT] Generating video script...")
    print("=" * 60)

    pages = generate_script(topic, num_pages=num_pages)
    write_project_yaml(pages, output_path, topic=topic,
                       style_prompt=style_prompt, tts_voice=tts_voice)

    print(f"\n[SCRIPT] Done! Edit {output_path} then run:")
    print(f"  python3 scripts/pipeline.py --config {output_path}")

    return output_path
