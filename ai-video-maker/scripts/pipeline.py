#!/usr/bin/env python3
"""
AI Video Maker — Pipeline Orchestrator

Usage:
    # Full pipeline
    python3 pipeline.py --config project.yaml

    # Run specific steps
    python3 pipeline.py --config project.yaml --steps tts images

    # Process specific pages only
    python3 pipeline.py --config project.yaml --steps tts --pages 1 2 5

    # Use resolution preset
    python3 pipeline.py --config project.yaml --preset shorts

    # Generate script from topic
    python3 pipeline.py --generate-script "AI发展简史" --config output/project.yaml

    # Validate only (no generation)
    python3 pipeline.py --config project.yaml --validate-only

    # Force re-run (ignore checkpoint)
    python3 pipeline.py --config project.yaml --no-resume
"""

import argparse
import os
import sys

# Add script directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, resolve_paths, ensure_dirs


ALL_STEPS = ["tts", "images", "subtitles", "segments", "merge", "bgm"]


def step_tts(config, paths, page_nums=None, checkpoint=None):
    """Step 1: Generate TTS audio for each page."""
    from tts_service import create_tts_provider, generate_tts_with_retry

    print("\n" + "=" * 60)
    print("[TTS] Generating voiceover audio...")
    print("=" * 60)

    provider = create_tts_provider(config.tts)
    success_count = 0

    for page_cfg in config.pages:
        p = page_cfg.page
        if page_nums and p not in page_nums:
            continue

        # Check checkpoint
        if checkpoint and checkpoint.is_completed(p, "tts"):
            print(f"  Page {p:02d}: checkpoint says done, skipping")
            success_count += 1
            continue

        output = os.path.join(paths["audio_dir"], f"page_{p:02d}.wav")
        if os.path.exists(output):
            print(f"  Page {p:02d}: already exists, skipping")
            success_count += 1
            if checkpoint:
                checkpoint.mark_completed(p, "tts")
            continue

        print(f"  Page {p:02d}: generating ({len(page_cfg.narration)} chars)...")
        ok = generate_tts_with_retry(provider, page_cfg.narration, output, config.tts)
        if ok:
            print(f"  Page {p:02d}: done")
            success_count += 1
            if checkpoint:
                checkpoint.mark_completed(p, "tts")
        else:
            print(f"  Page {p:02d}: FAILED")
            if checkpoint:
                checkpoint.mark_failed(p, "tts", "TTS generation failed")

    print(f"\n[TTS] {success_count}/{len(config.pages)} pages generated")
    return success_count > 0


def step_images(config, paths, page_nums=None, checkpoint=None):
    """Step 2: Generate AI images for each page."""
    from image_service import create_image_provider, generate_image_with_retry

    print("\n" + "=" * 60)
    print("[IMAGES] Generating images...")
    print("=" * 60)

    provider = create_image_provider(config.image_gen, config.video)
    success_count = 0

    for page_cfg in config.pages:
        p = page_cfg.page
        if page_nums and p not in page_nums:
            continue

        if checkpoint and checkpoint.is_completed(p, "images"):
            print(f"  Page {p:02d}: checkpoint says done, skipping")
            success_count += 1
            continue

        output = os.path.join(paths["images_dir"], f"page_{p:02d}.png")
        if os.path.exists(output):
            print(f"  Page {p:02d}: already exists, skipping")
            success_count += 1
            if checkpoint:
                checkpoint.mark_completed(p, "images")
            continue

        if not page_cfg.image_prompt:
            print(f"  Page {p:02d}: no image_prompt, skipping")
            continue

        print(f"  Page {p:02d}: generating...")
        ok = generate_image_with_retry(provider, page_cfg.image_prompt, output, config.image_gen)
        if ok:
            print(f"  Page {p:02d}: done")
            success_count += 1
            if checkpoint:
                checkpoint.mark_completed(p, "images")
        else:
            print(f"  Page {p:02d}: FAILED")
            if checkpoint:
                checkpoint.mark_failed(p, "images", "Image generation failed")

    print(f"\n[IMAGES] {success_count}/{len(config.pages)} pages generated")
    return success_count > 0


def step_subtitles(config, paths, page_nums=None, checkpoint=None):
    """Step 3: Process subtitles — static (burn to image) or dynamic (generate ASS)."""

    is_dynamic = config.subtitle.mode == "dynamic"

    print("\n" + "=" * 60)
    if is_dynamic:
        print("[SUBTITLES] Generating dynamic ASS subtitles...")
    else:
        print("[SUBTITLES] Burning subtitles to images...")
    print("=" * 60)

    success_count = 0

    for page_cfg in config.pages:
        p = page_cfg.page
        if page_nums and p not in page_nums:
            continue

        if checkpoint and checkpoint.is_completed(p, "subtitles"):
            print(f"  Page {p:02d}: checkpoint says done, skipping")
            success_count += 1
            continue

        # Find source image (png or jpg)
        src = os.path.join(paths["images_dir"], f"page_{p:02d}.png")
        if not os.path.exists(src):
            src = os.path.join(paths["images_dir"], f"page_{p:02d}.jpg")

        if is_dynamic:
            # Dynamic mode: generate ASS subtitle file
            aud = os.path.join(paths["audio_dir"], f"page_{p:02d}.wav")
            ass_out = os.path.join(paths["subtitles_dir"], f"page_{p:02d}.ass")

            if not os.path.exists(aud):
                print(f"  Page {p:02d}: no audio found for alignment")
                continue

            if not page_cfg.subtitle:
                print(f"  Page {p:02d}: no subtitle text, skipping")
                continue

            # Copy original image to images_sub (no burn)
            dst = os.path.join(paths["images_sub_dir"], f"page_{p:02d}.png")
            if os.path.exists(src):
                from shutil import copy2
                copy2(src, dst)

            # Generate ASS
            from subtitle_service import generate_dynamic_subtitle
            print(f"  Page {p:02d}: aligning...")
            ok = generate_dynamic_subtitle(
                audio_path=aud,
                narration_text=page_cfg.narration,
                subtitle_text=page_cfg.subtitle,
                ass_output_path=ass_out,
                config=config.subtitle,
                video_width=config.video.width,
                video_height=config.video.height,
            )
            if ok:
                print(f"  Page {p:02d}: done ({ass_out})")
                success_count += 1
                if checkpoint:
                    checkpoint.mark_completed(p, "subtitles")
            else:
                print(f"  Page {p:02d}: FAILED")
                if checkpoint:
                    checkpoint.mark_failed(p, "subtitles", "ASS generation failed")
        else:
            # Static mode: burn subtitle to image
            dst = os.path.join(paths["images_sub_dir"], f"page_{p:02d}.png")

            if not os.path.exists(src):
                print(f"  Page {p:02d}: no source image found")
                continue

            if not page_cfg.subtitle:
                from shutil import copy2
                copy2(src, dst)
                print(f"  Page {p:02d}: no subtitle, copied original")
                success_count += 1
                if checkpoint:
                    checkpoint.mark_completed(p, "subtitles")
                continue

            from subtitle_service import burn_subtitle
            burn_subtitle(src, dst, page_cfg.subtitle, config.subtitle)
            print(f"  Page {p:02d}: done")
            success_count += 1
            if checkpoint:
                checkpoint.mark_completed(p, "subtitles")

    print(f"\n[SUBTITLES] {success_count}/{len(config.pages)} pages processed")
    return success_count > 0


def step_segments(config, paths, page_nums=None, checkpoint=None):
    """Step 4: Create per-page video segments."""
    from tts_service import verify_audio
    from video_service import create_segment

    is_dynamic = config.subtitle.mode == "dynamic"

    print("\n" + "=" * 60)
    print("[SEGMENTS] Creating video segments...")
    print("=" * 60)

    seg_files = []
    durations = []

    for page_cfg in config.pages:
        p = page_cfg.page
        if page_nums and p not in page_nums:
            continue

        img = os.path.join(paths["images_sub_dir"], f"page_{p:02d}.png")
        aud = os.path.join(paths["audio_dir"], f"page_{p:02d}.wav")
        seg = os.path.join(paths["segments_dir"], f"page_{p:02d}.mp4")

        # Check if segment already exists (checkpoint or file)
        if os.path.exists(seg):
            from video_service import get_audio_duration
            dur = get_audio_duration(seg)
            seg_files.append(seg)
            durations.append(dur)
            print(f"  Page {p:02d}: already exists ({dur:.1f}s)")
            if checkpoint:
                checkpoint.mark_completed(p, "segments")
            continue

        if not os.path.exists(img) or not os.path.exists(aud):
            print(f"  Page {p:02d}: missing image or audio")
            continue

        if not verify_audio(aud):
            print(f"  Page {p:02d}: audio is SILENT, skipping")
            continue

        # Check for ASS subtitle (dynamic mode)
        ass_path = None
        if is_dynamic:
            ass_candidate = os.path.join(paths["subtitles_dir"], f"page_{p:02d}.ass")
            if os.path.exists(ass_candidate):
                ass_path = ass_candidate

        print(f"  Page {p:02d}: creating segment...", end=" ")
        ok, dur = create_segment(p, img, aud, seg, config.video, ass_path=ass_path)
        if ok:
            seg_files.append(seg)
            durations.append(dur)
            print(f"({dur:.1f}s)")
            if checkpoint:
                checkpoint.mark_completed(p, "segments")
        else:
            print("FAILED")
            if checkpoint:
                checkpoint.mark_failed(p, "segments", "Segment creation failed")

    # Store for merge step
    _cache["seg_files"] = seg_files
    _cache["durations"] = durations

    print(f"\n[SEGMENTS] {len(seg_files)}/{len(config.pages)} segments created")
    return len(seg_files) >= 2


def step_merge(config, paths, page_nums=None, checkpoint=None):
    """Step 5: Merge all segments with transitions."""
    from video_service import merge_segments

    print("\n" + "=" * 60)
    print("[MERGE] Merging segments into final video...")
    print("=" * 60)

    # Use cached segments or discover from directory
    seg_files = _cache.get("seg_files")
    durations = _cache.get("durations")

    if not seg_files:
        # Discover segments from directory
        from video_service import get_audio_duration
        seg_dir = paths["segments_dir"]
        files = sorted([
            f for f in os.listdir(seg_dir)
            if f.startswith("page_") and f.endswith(".mp4")
        ])
        seg_files = [os.path.join(seg_dir, f) for f in files]
        durations = [get_audio_duration(f) for f in seg_files]

    if len(seg_files) < 2:
        print("  Not enough segments to merge (need >= 2)")
        return False

    print(f"  Merging {len(seg_files)} segments...")
    ok = merge_segments(seg_files, durations, paths["output_path"], config.video)

    if ok:
        print(f"\n[MERGE] Success: {paths['output_path']}")
    return ok


def step_bgm(config, paths, page_nums=None, checkpoint=None):
    """Step 6: Add background music to final video."""
    if not config.bgm.enabled:
        print("\n[BGM] Disabled in config, skipping")
        return True

    if not config.bgm.file:
        print("\n[BGM] No BGM file specified, skipping")
        return True

    if not os.path.exists(config.bgm.file):
        print(f"\n[BGM] BGM file not found: {config.bgm.file}")
        return False

    from bgm_service import add_bgm_to_video

    print("\n" + "=" * 60)
    print("[BGM] Adding background music...")
    print("=" * 60)

    # Input: final video from merge step
    input_video = paths["output_path"]
    if not os.path.exists(input_video):
        print(f"  Video not found: {input_video}")
        return False

    # Output: save alongside
    output_video = os.path.join(paths["output_dir"], "final_with_bgm.mp4")

    ok = add_bgm_to_video(
        video_path=input_video,
        bgm_path=config.bgm.file,
        output_path=output_video,
        bgm_volume=config.bgm.volume,
        fade_in=config.bgm.fade_in,
        fade_out=config.bgm.fade_out,
    )

    if ok:
        print(f"\n[BGM] Success: {output_video}")
    return ok


# Cache for passing data between segments and merge steps
_cache = {}


def run_pipeline(config_path: str, steps: list[str] = None,
                 page_nums: list[int] = None, preset: str = None,
                 no_resume: bool = False, validate_only: bool = False):
    """Execute the pipeline with given config."""
    config = load_config(config_path)

    # Override resolution preset from CLI
    if preset:
        config.video.resolution_preset = preset
        from resolution_presets import get_preset
        p = get_preset(preset)
        config.video.width = p.width
        config.video.height = p.height
        if not config.video.adapt_strategy:
            config.video.adapt_strategy = p.adapt_strategy

    paths = resolve_paths(config)
    ensure_dirs(paths)

    # Setup checkpoint
    from checkpoint import CheckpointManager
    checkpoint = CheckpointManager(config.project_dir)
    if no_resume:
        checkpoint.reset()
        print("[CHECKPOINT] Reset — starting fresh")
    else:
        if checkpoint.load():
            print("[CHECKPOINT] Resuming from previous run")
            checkpoint.print_status()
    checkpoint.init_run(config_path)

    # Validate-only mode
    if validate_only:
        from validator import run_validation
        all_pages = [pc.page for pc in config.pages]
        report_path = os.path.join(config.project_dir, "validation_report.json")
        run_validation(paths, all_pages, output_report=report_path)
        return

    steps_to_run = steps or ALL_STEPS

    print("\n" + "=" * 60)
    print("AI Video Maker Pipeline")
    print("=" * 60)
    print(f"Config: {config_path}")
    print(f"Project: {config.project_dir}")
    print(f"Pages: {len(config.pages)}")
    print(f"Steps: {', '.join(steps_to_run)}")
    print(f"Resolution: {config.video.width}x{config.video.height}")
    if config.video.resolution_preset:
        print(f"Preset: {config.video.resolution_preset}")
    print(f"Subtitle mode: {config.subtitle.mode}")
    if config.bgm.enabled:
        print(f"BGM: {config.bgm.file} (vol={config.bgm.volume})")
    if page_nums:
        print(f"Page filter: {page_nums}")

    step_map = {
        "tts": step_tts,
        "images": step_images,
        "subtitles": step_subtitles,
        "segments": step_segments,
        "merge": step_merge,
        "bgm": step_bgm,
    }

    for step_name in steps_to_run:
        func = step_map.get(step_name)
        if not func:
            print(f"\nUnknown step: {step_name}. Available: {list(step_map.keys())}")
            continue
        ok = func(config, paths, page_nums, checkpoint=checkpoint)
        if not ok:
            print(f"\n[WARNING] Step '{step_name}' had issues. Continuing...")

    # Auto-validate after pipeline
    from validator import run_validation
    all_pages = page_nums or [pc.page for pc in config.pages]
    report_path = os.path.join(config.project_dir, "validation_report.json")
    run_validation(paths, all_pages, output_report=report_path)

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AI Video Maker Pipeline")
    parser.add_argument("--config", required=True, help="Path to project YAML config")
    parser.add_argument(
        "--steps", nargs="*", default=None,
        help=f"Run specific steps: {' '.join(ALL_STEPS)}",
    )
    parser.add_argument(
        "--pages", nargs="*", type=int, default=None,
        help="Process specific pages only (e.g., --pages 1 2 5)",
    )
    parser.add_argument(
        "--preset", default=None,
        help="Resolution preset: youtube, shorts, instagram, xiaohongshu, bilibili",
    )
    parser.add_argument(
        "--generate-script", metavar="TOPIC", default=None,
        help="Generate video script from topic, save to --config path",
    )
    parser.add_argument(
        "--num-pages", type=int, default=10,
        help="Number of pages for script generation (default: 10)",
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only run validation checks, no generation",
    )
    parser.add_argument(
        "--no-resume", action="store_true",
        help="Ignore checkpoint, force re-run all steps",
    )
    args = parser.parse_args()

    # Script generation mode
    if args.generate_script:
        from script_generator import generate_and_save
        generate_and_save(
            topic=args.generate_script,
            output_path=args.config,
            num_pages=args.num_pages,
        )
        return

    run_pipeline(
        args.config,
        steps=args.steps,
        page_nums=args.pages,
        preset=args.preset,
        no_resume=args.no_resume,
        validate_only=args.validate_only,
    )


if __name__ == "__main__":
    main()
