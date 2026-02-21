#!/usr/bin/env python3
"""Video composition service — Ken Burns, segments, transitions, merge."""

import os
import subprocess
import tempfile

from config import VideoConfig


def get_audio_duration(path: str) -> float:
    """Get audio/video duration in seconds via ffprobe."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def ken_burns_filter(page_idx: int, frames: int, config: VideoConfig) -> str:
    """Generate Ken Burns filter string — scale+crop, NOT zoompan."""
    W, H = config.width, config.height
    SW = int(W * config.kb_scale)
    SH = int(H * config.kb_scale)
    dx, dy = SW - W, SH - H

    effects = [
        # 0: Static centered
        f"scale={SW}:{SH},crop={W}:{H}:(ow-{W})/2:(oh-{H})/2",
        # 1: Top-left → Bottom-right
        f"scale={SW}:{SH},crop={W}:{H}:t/{frames}*{dx}:t/{frames}*{dy}",
        # 2: Static centered
        f"scale={SW}:{SH},crop={W}:{H}:(ow-{W})/2:(oh-{H})/2",
        # 3: Bottom-right → Top-left
        f"scale={SW}:{SH},crop={W}:{H}:{dx}-t/{frames}*{dx}:t/{frames}*{dy}",
    ]
    return effects[page_idx % 4]


def create_segment(page_num: int, image_path: str, audio_path: str,
                   output_path: str, config: VideoConfig,
                   ass_path: str = None) -> tuple[bool, float]:
    """Create a single page video segment with Ken Burns. Returns (success, duration).

    If ass_path is provided, overlays ASS subtitle (dynamic mode).
    """
    duration = get_audio_duration(audio_path) + config.buffer
    frames = int(duration * config.fps)
    kb = ken_burns_filter(page_num - 1, frames, config)

    # Build filter chain
    vf = f"[0:v]{kb},format=yuv420p"
    if ass_path and os.path.exists(ass_path):
        # Escape special chars in path for ffmpeg
        escaped_ass = ass_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        vf += f",ass='{escaped_ass}'"
    vf += "[v]"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-filter_complex", vf,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", config.preset, "-crf", str(config.crf),
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(config.fps), "-t", str(duration),
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        return True, duration
    else:
        print(f"    ffmpeg error: {r.stderr[-200:]}")
        return False, 0.0


def merge_segments(segment_files: list[str], durations: list[float],
                   output_path: str, config: VideoConfig) -> bool:
    """Merge segments with xfade transitions and fade in/out."""
    n = len(segment_files)
    if n < 2:
        print("Need at least 2 segments to merge")
        return False

    # Build inputs
    inputs = []
    for f in segment_files:
        inputs += ["-i", f]

    # Calculate offsets
    offsets = []
    cumulative = 0.0
    for i in range(n - 1):
        cumulative += durations[i]
        offsets.append(max(0, cumulative - (i + 1) * config.transition_dur))

    # Build video xfade chain
    fstr = ""
    prev = "[0:v]"
    for i in range(n - 1):
        ni = f"[{i+1}:v]"
        ol = f"[v{i}]" if i < n - 2 else "[vout]"
        trans = config.transitions[i % len(config.transitions)]
        fstr += f"{prev}{ni}xfade=transition={trans}:duration={config.transition_dur}:offset={offsets[i]:.3f}{ol};"
        prev = ol

    # Audio concat
    astr = "".join(f"[{i}:a]" for i in range(n))
    fstr += f"{astr}concat=n={n}:v=0:a=1[aout]"

    # Insert fade in/out before [vout]
    total_dur = sum(durations) - (n - 1) * config.transition_dur
    fade_out_start = max(0, total_dur - config.fade_out)
    fstr = fstr.replace(
        "[vout];",
        f"[vpre];[vpre]fade=t=in:st=0:d={config.fade_in},fade=t=out:st={fade_out_start:.3f}:d={config.fade_out}[vout];",
    )

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", fstr,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", config.preset, "-crf", str(config.crf),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        sz = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  Output: {output_path} ({sz:.1f}MB, ~{total_dur:.0f}s)")
        return True
    else:
        print(f"  xfade merge failed: {r.stderr[-300:]}")
        # Try fallback
        print("  Trying fallback concat...")
        return fallback_concat(segment_files, output_path, config)


def fallback_concat(segment_files: list[str], output_path: str,
                    config: VideoConfig = None) -> bool:
    """Simple concat fallback when xfade fails (no transitions)."""
    # Write concat list to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for seg in segment_files:
            f.write(f"file '{os.path.abspath(seg)}'\n")
        list_path = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", list_path,
            "-c:v", "libx264", "-preset", config.preset if config else "medium",
            "-crf", str(config.crf if config else 20),
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            sz = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  Fallback output: {output_path} ({sz:.1f}MB)")
            return True
        else:
            print(f"  Fallback concat also failed: {r.stderr[-300:]}")
            return False
    finally:
        os.unlink(list_path)
