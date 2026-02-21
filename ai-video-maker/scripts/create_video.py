#!/usr/bin/env python3
"""
DEPRECATED: 请使用 pipeline.py + YAML 配置代替。
  python3 scripts/pipeline.py --config project.yaml

本文件保留用于向后兼容。新项目请使用 pipeline.py。
"""
import os, subprocess, wave
from PIL import Image, ImageDraw, ImageFont

# ==================== CONFIG ====================

AUDIO_DIR = "audio"           # TTS 音频目录
IMAGES_DIR = "images"         # AI 图片目录
IMAGES_SUB = "images_sub"     # 烧字幕后（自动生成）
SEGMENTS = "segments"         # 单页片段（自动生成）
OUTPUT = "video/final_subtitled.mp4"

FPS = 30
TRANSITION_DUR = 0.8          # 转场时长（秒）
BUFFER = 0.5                  # 音频后额外停留（秒）
KB_SCALE = 1.08               # Ken Burns 缩放比例

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"  # 中文字体
FONT_SIZE = 36
BOX_ALPHA = 160               # 字幕底框透明度 (0-255)

FADE_IN = 1.0                 # 片头淡入（秒）
FADE_OUT = 1.5                # 片尾淡出（秒）

# 字幕文本 — 每页 2-3 行
SUBTITLES = {
    1: "第一页字幕\n第二行\n第三行",
    2: "第二页字幕\n...",
    # ... 按页数填写
}

# 转场效果循环
TRANSITIONS = ["fade", "fadeblack", "slideleft", "dissolve", "fadewhite"]

# ==================== FUNCTIONS ====================

def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())

def verify_audio(path):
    """验证音频不为空"""
    w = wave.open(path, 'rb')
    frames = w.readframes(min(w.getnframes(), 5000))
    w.close()
    if not frames:
        return False
    mx = max(abs(int.from_bytes(frames[i:i+2], 'little', signed=True))
             for i in range(0, len(frames), 2))
    return mx > 0

def burn_subtitle(src, dst, text):
    """Pillow 烧字幕到图片"""
    img = Image.open(src).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    lines = text.strip().split("\n")
    sizes = [draw.textbbox((0, 0), l, font=font) for l in lines]
    sizes = [(b[2]-b[0], b[3]-b[1]) for b in sizes]
    
    total_h = sum(h for _, h in sizes) + 10 * (len(lines) - 1)
    max_w = max(w for w, _ in sizes)
    
    pad = 14
    bx1 = (W - max_w) // 2 - pad
    by1 = H - 50 - total_h - pad
    bx2 = (W + max_w) // 2 + pad
    by2 = H - 50 + pad
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=(0, 0, 0, BOX_ALPHA))
    
    y = H - 50 - total_h
    for i, line in enumerate(lines):
        w, h = sizes[i]
        draw.text(((W - w) // 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += h + 10
    
    Image.alpha_composite(img, overlay).convert("RGB").save(dst, quality=95)

def ken_burns_filter(page_idx, frames):
    """Ken Burns 效果 — scale+crop（不用zoompan！）"""
    W, H = 1920, 1080
    SW, SH = int(W * KB_SCALE), int(H * KB_SCALE)
    dx, dy = SW - W, SH - H
    effects = [
        f"scale={SW}:{SH},crop={W}:{H}:(ow-{W})/2:(oh-{H})/2",
        f"scale={SW}:{SH},crop={W}:{H}:t/{frames}*{dx}:t/{frames}*{dy}",
        f"scale={SW}:{SH},crop={W}:{H}:(ow-{W})/2:(oh-{H})/2",
        f"scale={SW}:{SH},crop={W}:{H}:{dx}-t/{frames}*{dx}:t/{frames}*{dy}",
    ]
    return effects[page_idx % 4]

# ==================== MAIN ====================

def main():
    os.makedirs(IMAGES_SUB, exist_ok=True)
    os.makedirs(SEGMENTS, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT) or ".", exist_ok=True)
    
    # Discover pages
    pages = sorted([
        int(f.replace("page_", "").replace(".wav", ""))
        for f in os.listdir(AUDIO_DIR) if f.startswith("page_") and f.endswith(".wav")
    ])
    print(f"Found {len(pages)} pages: {pages}")
    
    # Step 1: Burn subtitles
    print("\n📝 Burning subtitles...")
    for p in pages:
        src = f"{IMAGES_DIR}/page_{p:02d}.png"
        dst = f"{IMAGES_SUB}/page_{p:02d}.png"
        if not os.path.exists(src):
            # Try jpg
            src = f"{IMAGES_DIR}/page_{p:02d}.jpg"
        if p in SUBTITLES and os.path.exists(src):
            burn_subtitle(src, dst, SUBTITLES[p])
            print(f"  ✅ Page {p:02d}")
        else:
            print(f"  ⚠️ Page {p:02d} — no subtitle or image")
    
    # Step 2: Create segments
    print("\n🎬 Creating segments...")
    seg_files, durs = [], []
    for p in pages:
        img = f"{IMAGES_SUB}/page_{p:02d}.png"
        aud = f"{AUDIO_DIR}/page_{p:02d}.wav"
        seg = f"{SEGMENTS}/page_{p:02d}.mp4"
        
        if not os.path.exists(img) or not os.path.exists(aud):
            print(f"  ⚠️ Page {p:02d} — missing files")
            continue
        
        if not verify_audio(aud):
            print(f"  ❌ Page {p:02d} — audio is SILENT!")
            continue
        
        dur = get_duration(aud) + BUFFER
        frames = int(dur * FPS)
        kb = ken_burns_filter(p - 1, frames)
        
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img, "-i", aud,
            "-filter_complex", f"[0:v]{kb},format=yuv420p[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-r", str(FPS), "-t", str(dur), seg
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            seg_files.append(seg)
            durs.append(dur)
            print(f"  ✅ Page {p:02d} ({dur:.1f}s)")
        else:
            print(f"  ❌ Page {p:02d}: {r.stderr[-150:]}")
    
    if len(seg_files) < 2:
        print("❌ Not enough segments to merge!")
        return
    
    # Step 3: Merge with xfade
    n = len(seg_files)
    print(f"\n🔀 Merging {n} segments with transitions...")
    
    inputs = []
    for f in seg_files:
        inputs += ["-i", f]
    
    offsets, cum = [], 0
    for i in range(n - 1):
        cum += durs[i]
        offsets.append(max(0, cum - (i + 1) * TRANSITION_DUR))
    
    fstr = ""
    prev = "[0:v]"
    for i in range(n - 1):
        ni = f"[{i+1}:v]"
        ol = f"[v{i}]" if i < n - 2 else "[vout]"
        trans = TRANSITIONS[i % len(TRANSITIONS)]
        fstr += f"{prev}{ni}xfade=transition={trans}:duration={TRANSITION_DUR}:offset={offsets[i]:.3f}{ol};"
        prev = ol
    
    astr = "".join(f"[{i}:a]" for i in range(n))
    fstr += f"{astr}concat=n={n}:v=0:a=1[aout]"
    
    # Add fade in/out
    total_dur = sum(durs) - (n - 1) * TRANSITION_DUR
    fstr = fstr.replace(
        "[vout];",
        f"[vpre];[vpre]fade=t=in:st=0:d={FADE_IN},fade=t=out:st={total_dur-FADE_OUT:.3f}:d={FADE_OUT}[vout];"
    )
    
    cmd = [
        "ffmpeg", "-y", *inputs, "-filter_complex", fstr,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUTPUT
    ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        sz = os.path.getsize(OUTPUT) / (1024 * 1024)
        print(f"\n🎉 Done! {OUTPUT} ({sz:.1f}MB, ~{total_dur:.0f}s)")
    else:
        print(f"❌ Merge failed: {r.stderr[-300:]}")

if __name__ == "__main__":
    main()
