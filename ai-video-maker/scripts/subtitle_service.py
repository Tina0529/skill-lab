#!/usr/bin/env python3
"""Subtitle burning service — outlined and boxed styles."""

from PIL import Image, ImageDraw, ImageFont

from config import SubtitleConfig


def _load_font(config: SubtitleConfig) -> ImageFont.FreeTypeFont:
    """Load font with fallback chain."""
    fallback_fonts = [
        config.font_path,
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in fallback_fonts:
        try:
            return ImageFont.truetype(fp, config.font_size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _measure_lines(draw: ImageDraw.ImageDraw, lines: list[str], font) -> list[tuple[int, int]]:
    """Measure width and height of each line."""
    sizes = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
    return sizes


def burn_subtitle_boxed(src_path: str, dst_path: str, text: str, config: SubtitleConfig) -> None:
    """Semi-transparent black box + white text style."""
    img = Image.open(src_path).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(config)

    lines = text.strip().split("\n")
    sizes = _measure_lines(draw, lines, font)

    total_h = sum(h for _, h in sizes) + config.line_spacing * (len(lines) - 1)
    max_w = max(w for w, _ in sizes)

    pad = config.box_padding
    # Box position: centered horizontally, margin_bottom from bottom
    bx1 = (W - max_w) // 2 - pad
    by1 = H - config.margin_bottom - total_h - pad
    bx2 = (W + max_w) // 2 + pad
    by2 = H - config.margin_bottom + pad
    draw.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=config.box_radius,
        fill=(0, 0, 0, config.box_alpha),
    )

    # Draw text lines
    y = H - config.margin_bottom - total_h
    for i, line in enumerate(lines):
        w, h = sizes[i]
        draw.text(((W - w) // 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += h + config.line_spacing

    Image.alpha_composite(img, overlay).convert("RGB").save(dst_path, quality=95)


def burn_subtitle_outlined(src_path: str, dst_path: str, text: str, config: SubtitleConfig) -> None:
    """White text with black outline, no background box."""
    img = Image.open(src_path).convert("RGBA")
    W, H = img.size

    # Optionally shrink image to make room for subtitles
    if config.image_shrink < 1.0:
        new_h = int(H * config.image_shrink)
        y_offset = int((H - new_h) * 0.35)
        resized = img.resize((W, new_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        canvas.paste(resized, (0, y_offset))
        img = canvas

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(config)

    lines = text.strip().split("\n")
    sizes = _measure_lines(draw, lines, font)

    total_h = sum(h for _, h in sizes) + config.line_spacing * (len(lines) - 1)
    ow = config.outline_width

    # Draw text with outline
    y = H - config.margin_bottom - total_h
    for i, line in enumerate(lines):
        w, h = sizes[i]
        x = (W - w) // 2

        # Black outline (8 directions)
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))

        # White text on top
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += h + config.line_spacing

    Image.alpha_composite(img, overlay).convert("RGB").save(dst_path, quality=95)


def burn_subtitle(src_path: str, dst_path: str, text: str, config: SubtitleConfig) -> None:
    """Dispatch to the appropriate subtitle style (static mode only)."""
    if config.style == "outlined":
        burn_subtitle_outlined(src_path, dst_path, text, config)
    else:
        burn_subtitle_boxed(src_path, dst_path, text, config)


def generate_dynamic_subtitle(audio_path: str, narration_text: str,
                               subtitle_text: str, ass_output_path: str,
                               config: SubtitleConfig,
                               video_width: int = 1920,
                               video_height: int = 1080) -> bool:
    """Generate ASS subtitle file using forced alignment (dynamic mode).

    Returns True on success.
    """
    from alignment_service import generate_dynamic_subtitles
    return generate_dynamic_subtitles(
        audio_path=audio_path,
        narration_text=narration_text,
        subtitle_text=subtitle_text,
        output_ass_path=ass_output_path,
        language=config.language,
        video_width=video_width,
        video_height=video_height,
        font_name=config.font_name,
        font_size=config.font_size,
        margin_bottom=config.margin_bottom,
        karaoke=config.karaoke,
    )
