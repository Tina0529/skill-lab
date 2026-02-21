#!/usr/bin/env python3
"""Configuration loading and validation for AI Video Maker pipeline."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class TTSConfig:
    provider: str = "gemini"           # "gemini" | "edge"
    voice: str = "Leda"                # Gemini: Leda/Kore/Aoede/Puck/Charon/Zephyr
    api_key_env: str = "GEMINI_API_KEY"
    speed: float = 1.0                 # atempo factor (1.0 = normal, 1.1 = slightly faster)
    max_retries: int = 3
    retry_delay: float = 5.0


@dataclass
class ImageGenConfig:
    provider: str = "gemini"           # "gemini" | "pillow_fallback"
    model: str = "gemini-3-pro-image-preview"
    api_key_env: str = "GEMINI_API_KEY"
    style_prompt: str = ""             # global style suffix appended to all prompts
    max_retries: int = 3
    retry_delay: float = 5.0


@dataclass
class SubtitleConfig:
    mode: str = "static"               # "static" (Pillow burn) | "dynamic" (ASS karaoke)
    style: str = "boxed"               # "outlined" | "boxed" (only for static mode)
    font_path: str = "/System/Library/Fonts/STHeiti Medium.ttc"
    font_name: str = "STHeiti"         # ASS font name (for dynamic mode)
    font_size: int = 36
    outline_width: int = 2             # for outlined style
    box_alpha: int = 160               # for boxed style (0-255)
    box_padding: int = 14
    box_radius: int = 8
    margin_bottom: int = 50
    line_spacing: int = 10
    image_shrink: float = 1.0          # 0.92 for outlined (shrink image), 1.0 for boxed
    karaoke: bool = True               # word-by-word highlighting (dynamic mode)
    language: str = "zh"               # language for alignment (dynamic mode)


@dataclass
class BGMConfig:
    enabled: bool = False
    file: str = ""                     # path to BGM audio file
    volume: float = 0.15               # BGM volume relative to voiceover
    fade_in: float = 2.0              # BGM fade-in duration (seconds)
    fade_out: float = 3.0             # BGM fade-out duration (seconds)


@dataclass
class VideoConfig:
    fps: int = 30
    width: int = 1920
    height: int = 1080
    resolution_preset: str = ""        # "" (use width/height) | "youtube" | "shorts" | etc.
    adapt_strategy: str = ""           # "" (auto from preset) | "crop_center" | "letterbox" | "blur_fill"
    kb_scale: float = 1.08             # Ken Burns scale factor
    transition_dur: float = 0.8
    transitions: list = field(default_factory=lambda: ["fade", "fadeblack", "slideleft", "dissolve", "fadewhite"])
    fade_in: float = 1.0
    fade_out: float = 1.5
    buffer: float = 0.5               # extra pause after audio ends
    crf: int = 20
    preset: str = "medium"             # libx264 preset


@dataclass
class PageConfig:
    page: int = 0
    narration: str = ""
    subtitle: str = ""
    image_prompt: str = ""


@dataclass
class ProjectConfig:
    project_dir: str = "."
    tts: TTSConfig = field(default_factory=TTSConfig)
    image_gen: ImageGenConfig = field(default_factory=ImageGenConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    bgm: BGMConfig = field(default_factory=BGMConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    pages: list = field(default_factory=list)  # list[PageConfig]


def _merge_dataclass(dc_class, data: dict):
    """Create a dataclass instance from dict, ignoring unknown fields."""
    if data is None:
        return dc_class()
    valid_fields = {f.name for f in dc_class.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in valid_fields}
    return dc_class(**filtered)


def load_config(yaml_path: str) -> ProjectConfig:
    """Load and validate YAML config, return ProjectConfig."""
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not raw:
        raise ValueError(f"Empty config file: {yaml_path}")

    config = ProjectConfig(
        project_dir=raw.get("project_dir", str(path.parent)),
        tts=_merge_dataclass(TTSConfig, raw.get("tts")),
        image_gen=_merge_dataclass(ImageGenConfig, raw.get("image_gen")),
        subtitle=_merge_dataclass(SubtitleConfig, raw.get("subtitle")),
        bgm=_merge_dataclass(BGMConfig, raw.get("bgm")),
        video=_merge_dataclass(VideoConfig, raw.get("video")),
    )

    # Apply resolution preset if specified
    if config.video.resolution_preset:
        from resolution_presets import get_preset
        preset = get_preset(config.video.resolution_preset)
        config.video.width = preset.width
        config.video.height = preset.height
        if not config.video.adapt_strategy:
            config.video.adapt_strategy = preset.adapt_strategy

    # Parse pages
    for p in raw.get("pages", []):
        config.pages.append(_merge_dataclass(PageConfig, p))

    # Validate
    if not config.pages:
        raise ValueError("Config must have at least one page in 'pages' array")

    for i, page in enumerate(config.pages):
        if not page.narration:
            raise ValueError(f"Page {page.page or i+1} is missing 'narration'")

    return config


def resolve_paths(config: ProjectConfig) -> dict:
    """Return dict of resolved directory paths for the project."""
    base = Path(config.project_dir)
    paths = {
        "project_dir": str(base),
        "audio_dir": str(base / "audio"),
        "images_dir": str(base / "images"),
        "images_sub_dir": str(base / "images_sub"),
        "subtitles_dir": str(base / "subtitles"),   # ASS subtitle files (dynamic mode)
        "segments_dir": str(base / "segments"),
        "output_dir": str(base / "video"),
        "output_path": str(base / "video" / "final_subtitled.mp4"),
    }
    return paths


def ensure_dirs(paths: dict) -> None:
    """Create all project directories."""
    for key in ["audio_dir", "images_dir", "images_sub_dir", "subtitles_dir", "segments_dir", "output_dir"]:
        os.makedirs(paths[key], exist_ok=True)
