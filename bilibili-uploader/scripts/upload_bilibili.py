#!/usr/bin/env python3
"""
B站视频自动上传脚本
基于 bilibili-api-python

使用流程：
1. 首次运行：python upload_bilibili.py login  (扫码登录，保存cookie)
2. 上传视频：python upload_bilibili.py upload --video xxx.mp4 --title "标题" --desc "简介" --tags "标签1,标签2"
3. 从meta.json上传：python upload_bilibili.py publish /path/to/content-folder/

依赖安装：
  pip install bilibili-api-python aiohttp
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path

# ============================================================
# 配置
# ============================================================
COOKIE_PATH = Path(__file__).parent / "cookie.json"

# B站常用分区 tid
TIDS = {
    "科技": 188,       # 科学科普
    "数码": 95,        # 数码
    "软件": 230,       # 软件应用
    "AI": 188,         # 科学科普（AI内容放这里）
    "资讯": 202,       # 资讯
    "日常": 21,        # 日常
    "影视": 183,       # 影视杂谈
    "教程": 36,        # 知识-社科人文
}
DEFAULT_TID = 188  # 科学科普


# ============================================================
# Cookie / 登录管理
# ============================================================
def save_credential(credential):
    """保存登录凭证到文件"""
    data = {
        "sessdata": credential.sessdata,
        "bili_jct": credential.bili_jct,
        "buvid3": credential.buvid3,
        "dedeuserid": credential.dedeuserid,
        "ac_time_value": credential.ac_time_value,
    }
    COOKIE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✅ Cookie已保存到 {COOKIE_PATH}")


def load_credential():
    """从文件加载登录凭证"""
    from bilibili_api import Credential
    if not COOKIE_PATH.exists():
        print("❌ 未找到cookie文件，请先运行: python upload_bilibili.py login")
        sys.exit(1)
    data = json.loads(COOKIE_PATH.read_text())
    return Credential(**data)


async def do_login():
    """扫码登录B站"""
    from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginEvents
    import shutil
    import tempfile

    print("🔐 B站扫码登录")
    print("正在生成二维码...")

    qr_login = QrCodeLogin()
    await qr_login.generate_qrcode()

    # 将二维码图片保存到桌面
    desktop_qr = Path.home() / "Desktop" / "bilibili_qr.png"
    tmp_qr = Path(tempfile.gettempdir()) / "qrcode.png"
    if tmp_qr.exists():
        shutil.copy2(str(tmp_qr), str(desktop_qr))
        print(f"\n📱 二维码已保存到桌面:")
        print(f"   {desktop_qr}")
        print(f"\n   请打开此图片，用B站APP扫码登录")
    else:
        # fallback: 终端显示
        try:
            terminal_str = qr_login.get_qrcode_terminal()
            print(terminal_str)
        except Exception:
            print("(二维码生成失败，请安装 qrcode: pip install qrcode)")

    print("\n等待扫码中...")

    # 轮询等待扫码
    while True:
        event = qr_login.check_state()
        if event == QrCodeLoginEvents.SCAN:
            print("  📱 已扫码，请在手机上确认...")
        elif event == QrCodeLoginEvents.CONF:
            print("  ✅ 已确认，正在登录...")
        elif event == QrCodeLoginEvents.DONE:
            break
        elif event == QrCodeLoginEvents.TIMEOUT:
            print("  ⏰ 二维码超时，请重新运行")
            sys.exit(1)
        await asyncio.sleep(2)

    credential = qr_login.get_credential()
    save_credential(credential)
    print("🎉 登录成功！")
    return credential


# ============================================================
# 上传功能
# ============================================================
async def upload_video(
    video_path: str,
    title: str,
    desc: str = "",
    tags: list = None,
    cover_path: str = None,
    tid: int = DEFAULT_TID,
    original: bool = False,
    source: str = "",
    delay_time: int = None,
):
    """上传视频到B站"""
    from bilibili_api.video_uploader import (
        VideoUploader,
        VideoUploaderPage,
        VideoUploaderEvents,
        VideoMeta,
    )

    credential = load_credential()

    # 检查credential是否有效
    try:
        from bilibili_api import Credential
        if not await credential.check_valid():
            print("⚠️ Cookie可能已过期，尝试刷新...")
            try:
                await credential.refresh()
                save_credential(credential)
                print("✅ Cookie已刷新")
            except Exception as e:
                print(f"❌ Cookie刷新失败: {e}")
                print("请重新登录: python upload_bilibili.py login")
                sys.exit(1)
    except Exception:
        pass  # check_valid 可能不可用，继续尝试上传

    if not tags:
        tags = ["AI", "科技"]

    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        sys.exit(1)

    print(f"📹 准备上传: {video_path.name}")
    print(f"   标题: {title}")
    print(f"   简介: {desc[:50]}..." if len(desc) > 50 else f"   简介: {desc}")
    print(f"   标签: {', '.join(tags)}")
    print(f"   分区: {tid}")
    print(f"   封面: {cover_path or '自动截取'}")
    print()

    # 创建分P
    page = VideoUploaderPage(
        path=str(video_path),
        title=title,
    )

    # 封面处理
    cover = cover_path or ""

    # 视频元数据
    meta_kwargs = dict(
        tid=tid,
        title=title,
        desc=desc,
        cover=cover,
        tags=tags,
        original=original,
        source=source if not original else None,
    )
    if delay_time:
        meta_kwargs["delay_time"] = delay_time
    meta = VideoMeta(**meta_kwargs)

    # 创建上传器
    uploader = VideoUploader(
        pages=[page],
        meta=meta,
        credential=credential,
        cover=cover,
    )

    # 注册事件回调（使用 .value 传字符串）
    @uploader.on(VideoUploaderEvents.PRE_PAGE.value)
    async def on_pre_page(data):
        print(f"  📤 开始上传分P...")

    @uploader.on(VideoUploaderEvents.AFTER_PAGE.value)
    async def on_after_page(data):
        print(f"  ✅ 分P上传完成")

    @uploader.on(VideoUploaderEvents.PRE_COVER.value)
    async def on_pre_cover(data):
        print(f"  🖼️ 上传封面...")

    @uploader.on(VideoUploaderEvents.PRE_SUBMIT.value)
    async def on_pre_submit(data):
        print(f"  📋 提交稿件...")

    @uploader.on(VideoUploaderEvents.COMPLETED.value)
    async def on_completed(data):
        print(f"\n🎉 上传成功！")
        if isinstance(data, dict):
            print(f"   BV号: {data.get('bvid', 'N/A')}")
            print(f"   AV号: {data.get('aid', 'N/A')}")
            print(f"   链接: https://www.bilibili.com/video/{data.get('bvid', '')}")

    @uploader.on(VideoUploaderEvents.FAILED.value)
    async def on_failed(data):
        print(f"\n❌ 上传失败: {data}")

    # 开始上传
    result = await uploader.start()
    return result


async def publish_from_meta(content_dir: str):
    """从content-pipeline的meta.json读取信息并上传"""
    content_dir = Path(content_dir)
    meta_path = content_dir / "meta.json"

    if not meta_path.exists():
        print(f"❌ 未找到 meta.json: {meta_path}")
        sys.exit(1)

    meta = json.loads(meta_path.read_text())

    # 查找视频文件
    video_file = None
    for ext in [".mp4", ".mkv", ".avi", ".mov", ".flv"]:
        candidates = list(content_dir.glob(f"*{ext}"))
        # 优先找 final 开头的
        final = [f for f in candidates if "final" in f.stem.lower()]
        if final:
            video_file = final[0]
            break
        if candidates:
            video_file = candidates[0]
            break

    if not video_file:
        print(f"❌ 未找到视频文件: {content_dir}")
        sys.exit(1)

    # 查找封面
    cover_file = None
    for name in ["cover.jpg", "cover.png", "thumbnail.jpg", "thumbnail.png"]:
        p = content_dir / name
        if p.exists():
            cover_file = str(p)
            break

    # 从meta提取信息
    title = meta.get("title_zh") or meta.get("title", video_file.stem)
    desc = meta.get("description_zh") or meta.get("description", "")
    tags = meta.get("tags", ["AI", "科技"])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    # 判断分区
    tid = meta.get("bilibili_tid", DEFAULT_TID)

    # 判断原创/转载
    original = meta.get("original", False)
    source = meta.get("source", "")

    print(f"📂 从 {content_dir.name} 发布")
    print(f"   视频: {video_file.name}")

    result = await upload_video(
        video_path=str(video_file),
        title=title,
        desc=desc,
        tags=tags,
        cover_path=cover_file,
        tid=tid,
        original=original,
        source=source,
    )

    # 更新meta.json
    if result:
        meta["bilibili_bvid"] = result.get("bvid")
        meta["bilibili_aid"] = result.get("aid")
        meta["bilibili_url"] = f"https://www.bilibili.com/video/{result.get('bvid', '')}"
        meta["status"] = "published"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        print(f"   📝 meta.json 已更新")

    return result


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="B站视频自动上传工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # login
    subparsers.add_parser("login", help="扫码登录B站")

    # upload
    upload_parser = subparsers.add_parser("upload", help="上传视频")
    upload_parser.add_argument("--video", "-v", required=True, help="视频文件路径")
    upload_parser.add_argument("--title", "-t", required=True, help="视频标题")
    upload_parser.add_argument("--desc", "-d", default="", help="视频简介")
    upload_parser.add_argument("--tags", default="AI,科技", help="标签，逗号分隔")
    upload_parser.add_argument("--cover", "-c", default=None, help="封面图片路径")
    upload_parser.add_argument("--tid", type=int, default=DEFAULT_TID, help=f"分区ID (默认{DEFAULT_TID})")
    upload_parser.add_argument("--original", action="store_true", help="标记为原创")
    upload_parser.add_argument("--source", default="", help="转载来源")
    upload_parser.add_argument("--delay", type=int, default=None, help="定时发布的Unix时间戳（秒）")

    # publish (从meta.json)
    publish_parser = subparsers.add_parser("publish", help="从content目录的meta.json上传")
    publish_parser.add_argument("content_dir", help="内容目录路径")

    # check (检查登录状态)
    subparsers.add_parser("check", help="检查登录状态")

    args = parser.parse_args()

    if args.command == "login":
        asyncio.run(do_login())

    elif args.command == "upload":
        tags = [t.strip() for t in args.tags.split(",")]
        asyncio.run(upload_video(
            video_path=args.video,
            title=args.title,
            desc=args.desc,
            tags=tags,
            cover_path=args.cover,
            tid=args.tid,
            original=args.original,
            source=args.source,
            delay_time=args.delay,
        ))

    elif args.command == "publish":
        asyncio.run(publish_from_meta(args.content_dir))

    elif args.command == "check":
        async def _check():
            cred = load_credential()
            try:
                valid = await cred.check_valid()
                if valid:
                    print("✅ Cookie有效")
                else:
                    print("⚠️ Cookie可能已过期，建议重新登录")
            except Exception as e:
                print(f"⚠️ 检查失败: {e}")
        asyncio.run(_check())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
