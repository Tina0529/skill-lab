#!/usr/bin/env python3
"""Forced alignment service — audio to word-level timestamps, ASS subtitle generation.

Uses WhisperX for forced alignment to produce word-level timestamps,
then generates ASS (Advanced SubStation Alpha) subtitles with karaoke effects.

Fallback: If WhisperX is not available, generates static ASS subtitles
based on even time division of the narration text.
"""

import os
import re
from dataclasses import dataclass


@dataclass
class WordTimestamp:
    word: str
    start: float  # seconds
    end: float    # seconds


@dataclass
class SubtitleSegment:
    text: str
    start: float
    end: float
    words: list  # list[WordTimestamp]


def _check_whisperx_available() -> bool:
    """Check if whisperx is installed."""
    try:
        import whisperx  # noqa: F401
        return True
    except ImportError:
        return False


def align_audio(audio_path: str, text: str, language: str = "zh") -> list[WordTimestamp]:
    """Run WhisperX forced alignment on audio with reference text.

    Returns list of WordTimestamp with per-word timing.
    Falls back to even division if WhisperX is unavailable.
    """
    if not _check_whisperx_available():
        print("  WhisperX not installed, using even-division fallback")
        return _fallback_even_division(audio_path, text)

    import whisperx
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "float32"

    # Step 1: Transcribe to get segments
    model = whisperx.load_model("base", device, compute_type=compute_type, language=language)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=16, language=language)

    # Step 2: Forced alignment
    align_model, align_metadata = whisperx.load_align_model(
        language_code=language, device=device
    )
    result = whisperx.align(
        result["segments"], align_model, align_metadata, audio, device,
        return_char_alignments=False
    )

    # Extract word timestamps
    words = []
    for segment in result.get("segments", []):
        for w in segment.get("words", []):
            if "start" in w and "end" in w:
                words.append(WordTimestamp(
                    word=w["word"].strip(),
                    start=w["start"],
                    end=w["end"],
                ))

    if not words:
        print("  WhisperX returned no word timestamps, using fallback")
        return _fallback_even_division(audio_path, text)

    return words


def _get_audio_duration(audio_path: str) -> float:
    """Get audio duration via ffprobe."""
    import subprocess
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0",
         audio_path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def _fallback_even_division(audio_path: str, text: str) -> list[WordTimestamp]:
    """Fallback: divide text evenly across audio duration."""
    duration = _get_audio_duration(audio_path)
    # Split text into characters (for Chinese) or words (for others)
    chars = list(text.replace("\n", "").replace(" ", ""))
    if not chars:
        return []

    char_dur = duration / len(chars)
    words = []
    for i, ch in enumerate(chars):
        words.append(WordTimestamp(
            word=ch,
            start=i * char_dur,
            end=(i + 1) * char_dur,
        ))
    return words


def group_words_into_segments(words: list[WordTimestamp], subtitle_text: str,
                              max_chars_per_line: int = 20) -> list[SubtitleSegment]:
    """Group word timestamps into display segments matching the subtitle text.

    Uses the subtitle_text lines as grouping guide.
    Each line of subtitle_text becomes one SubtitleSegment.
    """
    if not words:
        return []

    lines = [l.strip() for l in subtitle_text.strip().split("\n") if l.strip()]
    if not lines:
        return []

    segments = []
    word_idx = 0

    for line in lines:
        # Count characters in this line (excluding spaces)
        line_chars = len(line.replace(" ", ""))
        if line_chars == 0:
            continue

        # Collect words for this line
        seg_words = []
        chars_collected = 0

        while word_idx < len(words) and chars_collected < line_chars:
            w = words[word_idx]
            seg_words.append(w)
            chars_collected += len(w.word)
            word_idx += 1

        if seg_words:
            segments.append(SubtitleSegment(
                text=line,
                start=seg_words[0].start,
                end=seg_words[-1].end,
                words=seg_words,
            ))

    return segments


def _format_ass_time(seconds: float) -> str:
    """Format seconds to ASS time format: H:MM:SS.CC (centiseconds)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _centiseconds(seconds: float) -> int:
    """Convert seconds to centiseconds for \\k tag."""
    return max(1, int(seconds * 100))


def generate_ass_subtitle(segments: list[SubtitleSegment], output_path: str,
                          video_width: int = 1920, video_height: int = 1080,
                          font_name: str = "STHeiti",
                          font_size: int = 36,
                          primary_color: str = "&H00FFFFFF",
                          highlight_color: str = "&H0000FFFF",
                          outline_color: str = "&H00000000",
                          outline_width: int = 2,
                          margin_bottom: int = 50,
                          karaoke: bool = True) -> None:
    """Generate ASS subtitle file with optional karaoke word-by-word highlighting.

    karaoke=True: Words highlight progressively (\\k tags)
    karaoke=False: Static subtitles (no highlighting, just timed display)
    """
    header = f"""[Script Info]
Title: AI Video Maker Subtitles
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},{highlight_color},{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,{outline_width},1,2,10,10,{margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for seg in segments:
        start = _format_ass_time(seg.start)
        end = _format_ass_time(seg.end)

        if karaoke and seg.words and len(seg.words) > 1:
            # Build karaoke text with \k tags
            parts = []
            for w in seg.words:
                dur_cs = _centiseconds(w.end - w.start)
                parts.append(f"{{\\k{dur_cs}}}{w.word}")
            text = "".join(parts)
        else:
            text = seg.text

        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(events))
        f.write("\n")


def generate_dynamic_subtitles(audio_path: str, narration_text: str,
                               subtitle_text: str, output_ass_path: str,
                               language: str = "zh",
                               video_width: int = 1920,
                               video_height: int = 1080,
                               font_name: str = "STHeiti",
                               font_size: int = 36,
                               margin_bottom: int = 50,
                               karaoke: bool = True) -> bool:
    """High-level function: audio + text → ASS subtitle file.

    1. Run forced alignment on audio
    2. Group words into subtitle segments
    3. Generate ASS file

    Returns True on success.
    """
    try:
        # Step 1: Align
        print(f"    Aligning audio to text...")
        words = align_audio(audio_path, narration_text, language)
        if not words:
            print(f"    No words aligned")
            return False

        # Step 2: Group
        segments = group_words_into_segments(words, subtitle_text)
        if not segments:
            print(f"    No subtitle segments generated")
            return False

        # Step 3: Generate ASS
        generate_ass_subtitle(
            segments, output_ass_path,
            video_width=video_width, video_height=video_height,
            font_name=font_name, font_size=font_size,
            margin_bottom=margin_bottom, karaoke=karaoke,
        )
        print(f"    Generated {len(segments)} subtitle segments")
        return True

    except Exception as e:
        print(f"    Dynamic subtitle generation failed: {e}")
        return False
