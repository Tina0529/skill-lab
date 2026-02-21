#!/usr/bin/env python3
"""Image generation service with provider abstraction."""

import os
import time
from abc import ABC, abstractmethod

from PIL import Image, ImageDraw, ImageFont

from config import ImageGenConfig, VideoConfig


class ImageProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, output_path: str) -> bool:
        """Generate image from prompt. Returns True on success."""
        ...


class GeminiImage(ImageProvider):
    def __init__(self, config: ImageGenConfig):
        self.config = config
        api_key = os.environ.get(config.api_key_env, "")
        if not api_key:
            raise ValueError(f"Environment variable {config.api_key_env} not set")

        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=api_key)
        self.types = types

    def generate(self, prompt: str, output_path: str) -> bool:
        full_prompt = prompt
        if self.config.style_prompt:
            full_prompt = f"{prompt}. {self.config.style_prompt}"

        response = self.client.models.generate_content(
            model=self.config.model,
            contents=full_prompt,
            config=self.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return True
        return False


class PillowFallback(ImageProvider):
    def __init__(self, config: ImageGenConfig, video_config: VideoConfig = None):
        self.config = config
        self.width = video_config.width if video_config else 1920
        self.height = video_config.height if video_config else 1080

    def generate(self, prompt: str, output_path: str) -> bool:
        img = Image.new("RGB", (self.width, self.height), (20, 30, 60))
        draw = ImageDraw.Draw(img)

        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 48)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 48)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Extract a short title from prompt (first 20 chars)
        title = prompt[:20] + "..." if len(prompt) > 20 else prompt
        draw.text(
            (self.width // 2, self.height // 2),
            title, font=font, fill="white", anchor="mm",
        )
        img.save(output_path, quality=95)
        return True


def create_image_provider(config: ImageGenConfig, video_config: VideoConfig = None) -> ImageProvider:
    """Factory function for image provider."""
    if config.provider == "gemini":
        return GeminiImage(config)
    elif config.provider == "pillow_fallback":
        return PillowFallback(config, video_config)
    else:
        raise ValueError(f"Unknown image provider: {config.provider}. Options: gemini, pillow_fallback")


def verify_image(path: str, min_size: int = 200_000) -> bool:
    """Check image file size > min_size (real AI images are typically > 200KB)."""
    try:
        return os.path.exists(path) and os.path.getsize(path) > min_size
    except Exception:
        return False


def generate_image_with_retry(provider: ImageProvider, prompt: str, output_path: str,
                               config: ImageGenConfig) -> bool:
    """Generate image with retry and quality verification."""
    for attempt in range(1, config.max_retries + 1):
        try:
            success = provider.generate(prompt, output_path)
            if success and os.path.exists(output_path):
                # For Pillow fallback, skip size check
                if config.provider == "pillow_fallback":
                    return True
                if verify_image(output_path):
                    return True
                print(f"    Attempt {attempt}: image too small (likely fallback), retrying...")
            else:
                print(f"    Attempt {attempt}: generation failed, retrying...")
        except Exception as e:
            print(f"    Attempt {attempt} failed: {e}")

        if attempt < config.max_retries:
            time.sleep(config.retry_delay)

    # Final fallback: generate with Pillow if AI generation failed
    if config.provider != "pillow_fallback":
        print(f"    Falling back to Pillow placeholder...")
        fallback = PillowFallback(config)
        return fallback.generate(prompt, output_path)

    print(f"    FAILED after {config.max_retries} attempts")
    return False
