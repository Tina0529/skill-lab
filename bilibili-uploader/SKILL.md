---
name: bilibili-uploader
description: Upload videos to Bilibili (B站) automatically. Use when the user wants to publish, upload, or post videos to Bilibili/B站, check B站 login status, or manage B站 credentials. Also activate when processing content-pipeline folders that need B站 publishing.
---

# Bilibili Video Uploader

Upload videos to B站 via API using `bilibili-api-python`.

## Prerequisites

```bash
pip install bilibili-api-python aiohttp qrcode
```

## Script Location

`scripts/upload_bilibili.py` — main CLI tool.
Cookie stored at `scripts/cookie.json`.

---

## Workflow（严格按此流程执行）

### Step 0: 检查登录状态

每次上传前，先运行 `check` 命令确认 Cookie 是否有效：

```bash
python3 scripts/upload_bilibili.py check
```

- 如果输出 "Cookie有效" → 跳到 Step 1
- 如果输出 "过期" 或报错 → 执行登录流程（见下方"登录流程"）

### Step 1: 收集上传信息

**从用户消息或上下文中提取以下信息，缺失的项必须逐一询问用户：**

1. **视频文件路径** — "请提供要上传的视频文件路径"
2. **视频标题** — 最多 80 字
3. **视频简介** — 可基于上下文自动生成，但需用户确认
4. **标签** — 逗号分隔，至少 1 个，最多 10 个
5. **封面图片** — 可选，没有则 B站 自动截取
6. **分区** — 展示常用选项让用户选择
7. **原创/转载** — 转载需提供来源 URL

**Shortcut**: 如果用户一次性提供了所有信息，直接进入 Step 2。

### Step 2: 投稿信息预览确认（MANDATORY - 必须执行）

**在执行上传之前，必须将所有投稿信息以清晰的表格形式展示给用户确认。** 使用 AskUserQuestion 工具展示以下内容：

展示格式示例：

```
投稿信息预览：

| 项目 | 内容 |
|------|------|
| 视频文件 | /path/to/video.mp4 (大小: XX MB) |
| 标题 | xxxxxxxx |
| 简介 | xxxxxxxx |
| 标签 | tag1, tag2, tag3 |
| 封面 | /path/to/cover.png 或 "B站自动截取" |
| 分区 | 科学科普(188) |
| 类型 | 原创 / 转载（来源: xxx） |
```

然后询问："以上信息是否需要修改？"

- 如果用户要修改 → 根据用户反馈修改对应项，然后重新展示确认
- 如果用户确认无误 → 进入 Step 3

### Step 3: 选择发布方式（MANDATORY - 必须执行）

使用 AskUserQuestion 询问用户发布方式：

**问题: "请选择发布方式"**

选项：
1. **立即发布** — 上传后立即公开（审核通过后可见）
2. **定时发布** — 指定发布时间（需至少 2 小时后），追问具体时间
3. **暂不发布** — 仅上传视频和封面，不提交稿件。用户稍后可在 B站 创作中心手动发布

对于"定时发布"：
- 追问用户具体发布时间，格式如 "2026-02-20 18:00" 或 "明天下午6点"
- 将时间转换为 Unix 时间戳（秒）
- B站 要求定时发布时间至少在 2 小时之后
- 使用 `--delay <timestamp>` 参数

对于"暂不发布"：
- 告知用户：B站 API 不直接支持存草稿，但视频上传后可在 B站 创作中心 (member.bilibili.com) 的"草稿箱"中找到未提交的稿件进行编辑和发布
- 如果用户确实想存草稿，建议先不执行上传，等准备好了再来

### Step 4: 执行上传

所有确认完成后，执行上传命令：

```bash
python3 scripts/upload_bilibili.py upload \
  --video "<视频路径>" \
  --title "<标题>" \
  --desc "<简介>" \
  --tags "<标签1,标签2>" \
  --cover "<封面路径>" \
  --tid <分区ID> \
  --original \
  --delay <Unix时间戳>  # 仅定时发布时添加
```

上传完成后，向用户展示结果：BV号、链接等。

---

## 登录流程

当需要登录时，直接运行脚本（不要让用户手动执行）：

```bash
python3 scripts/upload_bilibili.py login
```

**二维码图片会自动保存到用户桌面**，路径为：`~/Desktop/bilibili_qr.png`

执行后，立即告知用户：
> "二维码已保存到你的桌面：`~/Desktop/bilibili_qr.png`，请打开图片用 B站 APP 扫码登录。"

等待脚本输出登录成功后，通知用户登录已完成。

**注意**：
- 不要让用户手动执行脚本，skill 应全程自动处理
- 如果登录超时（120秒），重新执行一次

---

## Common Partition IDs (tid)

| Category | tid | 适用内容 |
|----------|-----|---------|
| 科学科普 | 188 | AI、科技、科普 |
| 数码 | 95 | 数码产品评测 |
| 软件应用 | 230 | 软件教程、工具 |
| 资讯 | 202 | 新闻资讯 |
| 日常 | 21 | 日常vlog |
| 影视杂谈 | 183 | 影视评论 |
| 社科人文 | 36 | 教程、知识分享 |

---

## Publish from content-pipeline

当用户提供 content-pipeline 目录时：

1. 读取 `meta.json` 提取信息
2. 自动查找视频文件（优先 `final_*.mp4`）和封面
3. **仍然执行 Step 2（信息预览确认）和 Step 3（发布方式选择）**
4. 上传成功后更新 `meta.json`

```bash
python3 scripts/upload_bilibili.py publish <content-dir>
```

---

## Troubleshooting

- **Cookie expired**: 重新执行登录流程
- **Upload timeout**: 大文件上传可能需要较长时间，耐心等待
- **标签错误**: 确保标签不含特殊字符，每个标签不超过 20 字
- **标题过长**: B站 标题限制 80 字
- **定时发布失败**: 确保时间至少在 2 小时之后
