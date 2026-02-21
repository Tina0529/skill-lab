# Bilibili Uploader

B站视频自动上传工具。支持 QR 码扫描登录、视频上传、定时发布。

## 功能特点

- **QR 码登录**：二维码自动保存到桌面，扫码即用
- **视频上传**：支持标题、简介、标签、封面、分区设置
- **定时发布**：设定发布时间，B站自动定时公开
- **登录状态检查**：自动检测 Cookie 是否有效
- **Claude Code Skill**：作为 Skill 使用时，自动引导完成全部流程

## 快速开始

### 1. 安装依赖

```bash
pip install bilibili-api-python aiohttp qrcode
```

### 2. 首次登录

```bash
python3 scripts/upload_bilibili.py login
```

二维码自动保存到 `~/Desktop/bilibili_qr.png`，用 B站 APP 扫码登录。登录凭证保存在 `scripts/cookie.json`。

### 3. 上传视频

```bash
python3 scripts/upload_bilibili.py upload \
  --video /path/to/video.mp4 \
  --title "视频标题" \
  --desc "视频简介" \
  --tags "标签1,标签2,标签3" \
  --tid 188 \
  --original
```

### 4. 定时发布

```bash
# --delay 参数为 Unix 时间戳（至少 2 小时后）
python3 scripts/upload_bilibili.py upload \
  --video /path/to/video.mp4 \
  --title "视频标题" \
  --desc "视频简介" \
  --tags "标签1,标签2" \
  --tid 188 \
  --original \
  --delay 1740000000
```

## 命令说明

| 命令 | 用途 |
|------|------|
| `login` | QR 码扫描登录，保存 Cookie |
| `check` | 检查登录状态是否有效 |
| `upload` | 上传视频到 B站 |

## Upload 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--video` | 是 | 视频文件路径 |
| `--title` | 是 | 视频标题（最多 80 字） |
| `--desc` | 否 | 视频简介 |
| `--tags` | 否 | 标签，逗号分隔（最多 10 个） |
| `--cover` | 否 | 封面图片路径（不提供则 B站 自动截取） |
| `--tid` | 否 | 分区 ID（默认 188 科学科普） |
| `--original` | 否 | 标记为原创 |
| `--source` | 否 | 转载来源 URL（与 --original 互斥） |
| `--delay` | 否 | 定时发布的 Unix 时间戳 |

## 常用分区 ID

| 分区 | tid | 适用内容 |
|------|-----|---------|
| 科学科普 | 188 | AI、科技、科普 |
| 数码 | 95 | 数码产品评测 |
| 软件应用 | 230 | 软件教程、工具 |
| 资讯 | 202 | 新闻资讯 |
| 日常 | 21 | 日常 vlog |
| 影视杂谈 | 183 | 影视评论 |
| 社科人文 | 36 | 教程、知识分享 |

## 项目结构

```
bilibili-uploader/
├── SKILL.md                    # Claude Code Skill 定义
├── README.md                   # 本文档
└── scripts/
    └── upload_bilibili.py      # 主脚本
```

> `scripts/cookie.json` 为登录凭证，已加入 .gitignore，不会提交到仓库。

## 作为 Claude Code Skill 使用

安装到 `~/.claude/skills/bilibili-uploader/` 后，在 Claude Code 中说"上传视频到B站"即可自动激活。Skill 会引导你完成：

1. 检查登录状态
2. 收集上传信息（标题、简介、标签、分区等）
3. 投稿信息预览确认
4. 选择发布方式（立即 / 定时 / 暂不发布）
5. 执行上传

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| Cookie 过期 | 重新执行 `login` 命令 |
| 上传超时 | 大文件需要较长时间，耐心等待 |
| 标题过长 | B站 限制 80 字 |
| 定时发布失败 | 确保时间至少在 2 小时之后 |
| QR 码看不到 | 检查 `~/Desktop/bilibili_qr.png` |

## 技术栈

- Python 3.10+
- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api)
- aiohttp
- qrcode

## License

MIT
