#!/usr/bin/env python3
"""Resolution presets and image adaptation strategies for multi-format video output."""

import subprocess
from dataclasses import dataclass


@dataclass
class ResolutionPreset:
    name: str
    width: int
    height: int
    description: str
    adapt_strategy: str = "crop_center"  # crop_center | letterbox | blur_fill


# --- Presets ---

PRESETS = {
    "youtube": ResolutionPreset(
        name="youtube", width=1920, height=1080,
        description="YouTube landscape (16:9)",
        adapt_strategy="crop_center",
    ),
    "shorts": ResolutionPreset(
        name="shorts", width=1080, height=1920,
        description="YouTube Shorts / TikTok (9:16)",
        adapt_strategy="blur_fill",
    ),
    "instagram": ResolutionPreset(
        name="instagram", width=1080, height=1080,
        description="Instagram square (1:1)",
        adapt_strategy="crop_center",
    ),
    "xiaohongshu": ResolutionPreset(
        name="xiaohongshu", width=1080, height=1440,
        description="Xiaohongshu / Pinterest (3:4)",
        adapt_strategy="blur_fill",
    ),
    "bilibili": ResolutionPreset(
        name="bilibili", width=1920, height=1080,
        description="Bilibili landscape (16:9)",
        adapt_strategy="crop_center",
    ),
}


def get_preset(name: str) -> ResolutionPreset:
    """Get a resolution preset by name. Raises ValueError if not found."""
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]


def list_presets() -> list[ResolutionPreset]:
    """Return all available presets."""
    return list(PRESETS.values())


# --- Image Adaptation ---

def adapt_image_crop_center(input_path: str, output_path: str,
                            target_w: int, target_h: int) -> bool:
    """Scale to fill target then center-crop. Best for same-orientation images."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
               f"crop={target_w}:{target_h}",
        "-frames:v", "1", output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def adapt_image_letterbox(input_path: str, output_path: str,
                          target_w: int, target_h: int) -> bool:
    """Scale to fit inside target, pad with black bars. Preserves full image."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
               f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black",
        "-frames:v", "1", output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def adapt_image_blur_fill(input_path: str, output_path: str,
                          target_w: int, target_h: int) -> bool:
    """Blurred enlarged version as background + original centered. No black bars."""
    # Two passes: blurred background scaled to fill + sharp foreground scaled to fit
    vf = (
        f"split[bg][fg];"
        f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
        f"crop={target_w}:{target_h},boxblur=20:5[bg_out];"
        f"[fg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease[fg_out];"
        f"[bg_out][fg_out]overlay=(W-w)/2:(H-h)/2"
    )
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter_complex", vf,
        "-frames:v", "1", output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def adapt_image(input_path: str, output_path: str,
                target_w: int, target_h: int, strategy: str = "crop_center") -> bool:
    """Adapt image to target resolution using specified strategy."""
    strategies = {
        "crop_center": adapt_image_crop_center,
        "letterbox": adapt_image_letterbox,
        "blur_fill": adapt_image_blur_fill,
    }
    func = strategies.get(strategy)
    if not func:
        available = ", ".join(strategies.keys())
        raise ValueError(f"Unknown strategy '{strategy}'. Available: {available}")
    return func(input_path, output_path, target_w, target_h)
