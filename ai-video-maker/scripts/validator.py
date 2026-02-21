#!/usr/bin/env python3
"""Quality validation service — check all generated assets before final output."""

import json
import os
import subprocess
import wave
from dataclasses import dataclass, field, asdict


@dataclass
class CheckResult:
    name: str
    status: str = "pass"     # "pass" | "warning" | "error"
    severity: str = "info"   # "info" | "low" | "medium" | "high" | "critical"
    message: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    project_dir: str = ""
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    checks: list = field(default_factory=list)  # list[CheckResult]

    def add(self, check: CheckResult):
        self.checks.append(check)
        self.total_checks += 1
        if check.status == "pass":
            self.passed += 1
        elif check.status == "warning":
            self.warnings += 1
        elif check.status == "error":
            self.errors += 1


def _get_duration(path: str) -> float:
    """Get media duration via ffprobe."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


def check_audio_files(audio_dir: str, page_nums: list[int]) -> list[CheckResult]:
    """Validate audio files: existence, silence, duration range."""
    results = []

    for p in page_nums:
        path = os.path.join(audio_dir, f"page_{p:02d}.wav")

        # Existence check
        if not os.path.exists(path):
            results.append(CheckResult(
                name=f"audio_page_{p:02d}_exists",
                status="error", severity="critical",
                message=f"Audio file missing: {path}",
            ))
            continue

        # Size check
        size = os.path.getsize(path)
        if size < 1000:
            results.append(CheckResult(
                name=f"audio_page_{p:02d}_size",
                status="error", severity="high",
                message=f"Audio file too small ({size} bytes)",
            ))
            continue

        # Silence check
        try:
            w = wave.open(path, "rb")
            frames = w.readframes(min(w.getnframes(), 5000))
            w.close()
            if frames:
                mx = max(abs(int.from_bytes(frames[i:i+2], "little", signed=True))
                         for i in range(0, min(len(frames), 10000), 2))
                if mx == 0:
                    results.append(CheckResult(
                        name=f"audio_page_{p:02d}_silence",
                        status="error", severity="high",
                        message="Audio is completely silent",
                    ))
                    continue
        except Exception as e:
            results.append(CheckResult(
                name=f"audio_page_{p:02d}_read",
                status="warning", severity="medium",
                message=f"Cannot read audio: {e}",
            ))
            continue

        # Duration check (15-35s recommended, warn outside 5-60s)
        dur = _get_duration(path)
        if dur < 5:
            results.append(CheckResult(
                name=f"audio_page_{p:02d}_duration",
                status="warning", severity="medium",
                message=f"Audio very short ({dur:.1f}s)",
                details={"duration": dur},
            ))
        elif dur > 60:
            results.append(CheckResult(
                name=f"audio_page_{p:02d}_duration",
                status="warning", severity="low",
                message=f"Audio very long ({dur:.1f}s)",
                details={"duration": dur},
            ))
        else:
            results.append(CheckResult(
                name=f"audio_page_{p:02d}",
                status="pass",
                message=f"OK ({dur:.1f}s, {size/1024:.0f}KB)",
                details={"duration": dur, "size": size},
            ))

    return results


def check_image_files(images_dir: str, page_nums: list[int],
                      min_size: int = 200_000) -> list[CheckResult]:
    """Validate image files: existence, size, format."""
    results = []

    for p in page_nums:
        path = os.path.join(images_dir, f"page_{p:02d}.png")
        if not os.path.exists(path):
            path = os.path.join(images_dir, f"page_{p:02d}.jpg")
        if not os.path.exists(path):
            results.append(CheckResult(
                name=f"image_page_{p:02d}_exists",
                status="error", severity="critical",
                message=f"Image file missing",
            ))
            continue

        size = os.path.getsize(path)
        if size < min_size:
            results.append(CheckResult(
                name=f"image_page_{p:02d}_quality",
                status="warning", severity="medium",
                message=f"Image may be fallback/placeholder ({size/1024:.0f}KB < {min_size/1024:.0f}KB)",
                details={"size": size},
            ))
        else:
            results.append(CheckResult(
                name=f"image_page_{p:02d}",
                status="pass",
                message=f"OK ({size/1024:.0f}KB)",
                details={"size": size},
            ))

    return results


def check_final_video(video_path: str, expected_pages: int) -> list[CheckResult]:
    """Validate final video: existence, duration, codec."""
    results = []

    if not os.path.exists(video_path):
        results.append(CheckResult(
            name="final_video_exists",
            status="error", severity="critical",
            message=f"Final video missing: {video_path}",
        ))
        return results

    size = os.path.getsize(video_path)
    size_mb = size / (1024 * 1024)
    dur = _get_duration(video_path)

    # Size check
    if size < 100_000:
        results.append(CheckResult(
            name="final_video_size",
            status="error", severity="high",
            message=f"Video too small ({size_mb:.1f}MB)",
        ))
    else:
        results.append(CheckResult(
            name="final_video_size",
            status="pass",
            message=f"OK ({size_mb:.1f}MB)",
            details={"size_mb": size_mb},
        ))

    # Duration check (rough: 15-35s per page)
    min_expected = expected_pages * 10
    max_expected = expected_pages * 45
    if dur < min_expected:
        results.append(CheckResult(
            name="final_video_duration",
            status="warning", severity="medium",
            message=f"Video shorter than expected ({dur:.0f}s for {expected_pages} pages)",
            details={"duration": dur},
        ))
    elif dur > max_expected:
        results.append(CheckResult(
            name="final_video_duration",
            status="warning", severity="low",
            message=f"Video longer than expected ({dur:.0f}s for {expected_pages} pages)",
            details={"duration": dur},
        ))
    else:
        results.append(CheckResult(
            name="final_video_duration",
            status="pass",
            message=f"OK ({dur:.0f}s)",
            details={"duration": dur},
        ))

    return results


def run_validation(paths: dict, page_nums: list[int],
                   output_report: str = None) -> ValidationReport:
    """Run all validation checks and optionally save report.

    Args:
        paths: Dict from config.resolve_paths()
        page_nums: List of page numbers to validate
        output_report: Optional path to save JSON report

    Returns:
        ValidationReport with all check results
    """
    report = ValidationReport(project_dir=paths.get("project_dir", ""))

    print("\n" + "=" * 60)
    print("[VALIDATE] Running quality checks...")
    print("=" * 60)

    # Audio checks
    print("\n  Audio files:")
    for r in check_audio_files(paths["audio_dir"], page_nums):
        report.add(r)
        icon = {"pass": "  ", "warning": "  ", "error": "  "}[r.status]
        print(f"    {icon} {r.name}: {r.message}")

    # Image checks
    print("\n  Image files:")
    for r in check_image_files(paths["images_dir"], page_nums):
        report.add(r)
        icon = {"pass": "  ", "warning": "  ", "error": "  "}[r.status]
        print(f"    {icon} {r.name}: {r.message}")

    # Final video check
    print("\n  Final video:")
    for r in check_final_video(paths["output_path"], len(page_nums)):
        report.add(r)
        icon = {"pass": "  ", "warning": "  ", "error": "  "}[r.status]
        print(f"    {icon} {r.name}: {r.message}")

    # Summary
    print(f"\n  Summary: {report.passed} passed, "
          f"{report.warnings} warnings, {report.errors} errors")

    # Save report
    if output_report:
        report_data = asdict(report)
        with open(output_report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"  Report saved: {output_report}")

    return report
