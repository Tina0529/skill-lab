#!/usr/bin/env python3
"""BGM (Background Music) service — loop/trim, mix with voiceover, fade in/out."""

import os
import subprocess
import tempfile


def get_duration(path: str) -> float:
    """Get media file duration in seconds."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def prepare_bgm(bgm_path: str, target_duration: float, output_path: str,
                 fade_in: float = 2.0, fade_out: float = 3.0) -> bool:
    """Loop/trim BGM to target duration with fade in/out.

    If BGM is shorter than target, it loops. If longer, it trims.
    Always applies fade-in at start and fade-out at end.
    """
    bgm_dur = get_duration(bgm_path)

    filters = []

    if bgm_dur < target_duration:
        # Need to loop: use aloop or concat
        loop_count = int(target_duration / bgm_dur) + 1
        # Use concat for cleaner looping
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for _ in range(loop_count):
                f.write(f"file '{os.path.abspath(bgm_path)}'\n")
            list_path = f.name

        # First loop via concat, then trim + fade
        fade_out_start = max(0, target_duration - fade_out)
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", list_path,
            "-af", f"atrim=0:{target_duration},"
                   f"afade=t=in:st=0:d={fade_in},"
                   f"afade=t=out:st={fade_out_start}:d={fade_out}",
            "-c:a", "aac", "-b:a", "128k",
            output_path,
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
            return r.returncode == 0
        finally:
            os.unlink(list_path)
    else:
        # Trim + fade
        fade_out_start = max(0, target_duration - fade_out)
        cmd = [
            "ffmpeg", "-y", "-i", bgm_path,
            "-af", f"atrim=0:{target_duration},"
                   f"afade=t=in:st=0:d={fade_in},"
                   f"afade=t=out:st={fade_out_start}:d={fade_out}",
            "-c:a", "aac", "-b:a", "128k",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0


def mix_audio(voiceover_path: str, bgm_path: str, output_path: str,
              voice_volume: float = 1.0, bgm_volume: float = 0.15) -> bool:
    """Mix voiceover with BGM using amix filter.

    voice_volume: volume multiplier for voiceover (default 1.0)
    bgm_volume: volume multiplier for BGM (default 0.15 for subtle background)
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", voiceover_path,
        "-i", bgm_path,
        "-filter_complex",
        f"[0:a]volume={voice_volume}[v];"
        f"[1:a]volume={bgm_volume}[b];"
        f"[v][b]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def add_bgm_to_video(video_path: str, bgm_path: str, output_path: str,
                     bgm_volume: float = 0.15,
                     fade_in: float = 2.0, fade_out: float = 3.0) -> bool:
    """Add BGM to a finished video that already has voiceover audio.

    This is the high-level function for the pipeline:
    1. Get video duration
    2. Prepare BGM (loop/trim + fade)
    3. Mix BGM with existing audio
    4. Replace audio track in video
    """
    video_dur = get_duration(video_path)

    # Prepare BGM to match video length
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp_bgm:
        tmp_bgm_path = tmp_bgm.name
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp_mixed:
        tmp_mixed_path = tmp_mixed.name

    try:
        # Step 1: Prepare BGM
        ok = prepare_bgm(bgm_path, video_dur, tmp_bgm_path, fade_in, fade_out)
        if not ok:
            print("  BGM preparation failed")
            return False

        # Step 2: Extract voiceover from video, mix with BGM, replace
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", tmp_bgm_path,
            "-filter_complex",
            f"[0:a]volume=1.0[v];"
            f"[1:a]volume={bgm_volume}[b];"
            f"[v][b]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            sz = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  BGM added: {output_path} ({sz:.1f}MB)")
            return True
        else:
            print(f"  BGM mixing failed: {r.stderr[-200:]}")
            return False
    finally:
        for p in [tmp_bgm_path, tmp_mixed_path]:
            if os.path.exists(p):
                os.unlink(p)
