---
name: lark-connector
description: |
  Lark 集成桥梁 — 为任何需要和 Lark 交互的功能提供即用的工具链和集成模式。

  涵盖：消息读写、群组管理、云文档读写、通知推送。

  触发条件（满足任一即触发）：
  - 用户要求发送/读取 Lark 消息
  - 用户要开发涉及 Lark 集成的新功能
  - 用户提及"Lark群"、"Lark通知"、"Lark文档"
  - 用户要求配置或调试 Lark MCP Server
  - 用户要做消息监控、自动回复、定时报告等功能

  触发词：Lark、lark、飞书、群消息、群组、lark通知、lark文档、消息监控、自动回复
---

# Lark Connector

Lark 集成桥梁。开发任何 Lark 相关功能时，参考此 skill 获取工具、模式和配置信息。

---

## 当前配置

| 项目 | 值 |
|------|-----|
| App ID | `<YOUR_LARK_APP_ID>` |
| App Secret | `<YOUR_LARK_APP_SECRET>` |
| MCP 配置文件 | `~/.claude/.mcp.json` |
| MCP Server 代码 | `~/.claude/plugins/cache/sparticle-skill-marketplace/lark-demand-collector/1.0.0/mcp-server/src/lark_mcp_server/` |
| 平台 | Lark（海外版，larksuite.com） |

### 已连接群组

| 群组名 | chat_id |
|--------|---------|
| （示例） | `oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

> 如需连接新群组：在 Lark 群设置 → Bots → Add Bot → 选择应用，然后用 `lark_list_chats` 获取 chat_id。

---

## 前置要求

### 1. 安装 MCP Server

```bash
cd ~/.claude/plugins/cache/sparticle-skill-marketplace/lark-demand-collector/1.0.0/mcp-server
pip install -e .
```

### 2. 配置 .mcp.json

在 `~/.claude/.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "lark": {
      "command": "python",
      "args": ["-m", "lark_mcp_server.server"],
      "cwd": "<MCP_SERVER_SRC_PATH>",
      "env": {
        "LARK_APP_ID": "<YOUR_LARK_APP_ID>",
        "LARK_APP_SECRET": "<YOUR_LARK_APP_SECRET>"
      }
    }
  }
}
```

### 3. Lark 开放平台配置

1. 创建应用并启用 **Bot** 能力（Features → Bot）
2. 开通所需权限（见下方权限清单）
3. 将机器人添加到目标群组

---

## 可用工具

### 消息类

| MCP 工具 | 功能 | 必需权限 |
|----------|------|----------|
| `lark_list_chats` | 列出机器人加入的所有群组 | `im:chat:readonly` |
| `lark_get_chat_info` | 获取群组详情（名称、类型、成员数） | `im:chat:readonly` |
| `lark_get_messages` | 读取群组消息（支持时间范围、分页） | `im:message.group_msg` |
| `lark_send_message` | 向群组发送消息（文本/富文本/卡片） | `im:message:send_as_bot` |
| `lark_search_user_messages` | 搜索指定用户相关的消息 | `im:message.group_msg` |
| `lark_get_user_info` | 获取用户信息 | `contact:user.base:readonly` |
| `lark_download_image` | 下载消息中的图片 | `im:message.group_msg` |
| `lark_download_images_batch` | 批量下载图片 | `im:message.group_msg` |

### 云文档类（MCP 工具）

| MCP 工具 | 功能 | 必需权限 |
|----------|------|----------|
| `lark_create_document` | 在指定目录创建文档并写入内容 | `docx:document` |
| `lark_upload_file` | 上传本地文件到指定目录 | `drive:drive` |

> 注意：目标目录的链接分享需设为「组织内获得链接的人可编辑」，应用才有写入权限。

### 云文档读取（OAuth 脚本）

云文档**读取**使用独立的 OAuth 用户授权模式（非 MCP 工具），通过脚本调用：

```bash
# 读取文档
python3 ~/.claude/skills/lark-doc-reader/scripts/fetch_lark_doc.py "https://xxx.larksuite.com/docx/TOKEN"

# 查看登录状态
python3 ~/.claude/skills/lark-doc-reader/scripts/fetch_lark_doc.py --status
```

| 操作 | 命令 | 必需权限 |
|------|------|----------|
| 读取 Docx 文档 | `fetch_lark_doc.py "URL"` | `docx:document:readonly` |
| 读取 Sheet 表格 | `fetch_lark_doc.py "URL"` | `sheets:spreadsheet:readonly` |
| 读取 Bitable 多维表格 | `fetch_lark_doc.py "URL"` | `bitable:app:readonly` |
| 读取 Wiki 知识库 | `fetch_lark_doc.py "URL"` | `wiki:wiki:readonly` |

支持的 URL 格式：
- `https://xxx.larksuite.com/docx/TOKEN`
- `https://xxx.larksuite.com/sheets/TOKEN`
- `https://xxx.larksuite.com/base/TOKEN`
- `https://xxx.larksuite.com/wiki/TOKEN`

> 首次使用需浏览器 OAuth 授权，之后 30 天内免授权。

### Webhook 发消息（备选）

不依赖 MCP，直接 HTTP 调用，适合简单通知场景：

```bash
curl -X POST "<WEBHOOK_URL>" \
  -H "Content-Type: application/json" \
  -d '{"msg_type": "text", "content": {"text": "消息内容"}}'
```

---

## 工具参数详解

### lark_get_messages

```
chat_id:     必填，群组ID
start_time:  可选，ISO格式 "2024-01-01T00:00:00Z" 或相对时间 "7d"
end_time:    可选，ISO格式，默认当前时间
page_size:   可选，每页条数，最大50
page_token:  可选，分页标记
```

### lark_send_message

```
chat_id:   必填，目标群组ID
content:   必填，纯文本消息内容
msg_type:  可选，默认 "text"，支持 "text" / "post" / "interactive"
```

富文本消息示例（msg_type="post"）：
```json
{
  "zh_cn": {
    "title": "标题",
    "content": [[
      {"tag": "text", "text": "正文内容"},
      {"tag": "a", "text": "链接", "href": "https://example.com"}
    ]]
  }
}
```

### lark_create_document

```
folder_token:  必填，目标目录的 folder_token
title:         必填，文档标题
content:       可选，文档内容（纯文本，换行自动分段）
```

### lark_upload_file

```
folder_token:  必填，目标目录的 folder_token
file_path:     必填，本地文件路径
file_name:     可选，上传后的文件名（默认使用原文件名）
```

### lark_search_user_messages

```
chat_id:          必填，群组ID
target_user_id:   必填，目标用户的 open_id
start_time:       可选，开始时间
end_time:         可选，结束时间
include_mentions: 可选，包含 @该用户的消息，默认 true
include_sent:     可选，包含该用户发送的消息，默认 true
include_replies:  可选，包含回复该用户的线程，默认 true
```

---

## 集成模式

### 模式 1: 消息监控 + 自动回复

场景：监控群消息，检测到特定内容后自动回复。

```python
# 1. 拉取最近消息
messages = lark_get_messages(chat_id="oc_xxx", start_time="1h")

# 2. 分析消息内容（Claude 自动分析）
# 例如：检测到有人 @机器人，或包含关键词

# 3. 自动回复
lark_send_message(chat_id="oc_xxx", content="收到，正在处理...")
```

适用：客服机器人、需求收集、任务分发

### 模式 2: 定时拉取 + 生成报告

场景：定期从群里拉取消息，生成结构化报告。

```
步骤：
1. lark_get_messages(chat_id, start_time="24h") 拉取过去24小时消息
2. Claude 分析消息内容，分类整理
3. 生成报告（Markdown / HTML）
4. lark_send_message() 将报告摘要发回群
5. （可选）lark_create_document() 写入云文档永久保存
```

适用：每日站会总结、周报、舆情分析

### 模式 3: 事件触发 → Lark 通知

场景：外部事件发生时，推送通知到 Lark 群。

```bash
# 方式 A: 通过 MCP 工具
lark_send_message(chat_id="oc_xxx", content="CI 构建成功")

# 方式 B: 通过 Webhook（更轻量，不依赖 MCP）
curl -X POST "<WEBHOOK_URL>" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"CI 构建成功"}}'
```

适用：CI/CD 通知、监控告警、定时任务完成通知

### 模式 4: 读取云文档作为上下文

场景：读取 Lark 文档内容，作为 Claude 的工作上下文。

```bash
# 读取文档内容
python3 ~/.claude/skills/lark-doc-reader/scripts/fetch_lark_doc.py \
  "https://xxx.larksuite.com/docx/ABC123"

# 输出到文件供 Claude 读取
python3 ~/.claude/skills/lark-doc-reader/scripts/fetch_lark_doc.py \
  "https://xxx.larksuite.com/docx/ABC123" --output /tmp/doc.md
```

适用：基于文档做分析、PRD 转代码、文档审校

### 模式 5: 写入云文档

场景：将 Claude 生成的内容写入 Lark 文档。

```
步骤：
1. Claude 生成内容（报告、分析、总结等）
2. lark_create_document(
     folder_token="<YOUR_FOLDER_TOKEN>",
     title="报告标题-日期",
     content="报告内容..."
   )
3. 返回文档链接给用户
```

上传本地文件：
```
lark_upload_file(
  folder_token="<YOUR_FOLDER_TOKEN>",
  file_path="/tmp/report.pdf"
)
```

适用：自动生成会议纪要、报告归档、知识库更新

### 模式 6: 智能员工（消息驱动工作流）

场景：Claude 作为 Lark 群里的智能员工，接收任务并执行。

```
完整流程：
1. lark_get_messages() 定期拉取群消息
2. Claude 识别出任务指令（如 "@bot 帮我查一下XXX"）
3. Claude 执行任务（搜索、分析、写代码等）
4. lark_send_message() 将结果发回群
5. （可选）fetch_lark_doc.py 读取相关文档作为上下文
6. （可选）lark_create_document() 将结果写入云文档归档
```

---

## 权限清单

### 消息相关权限

| 权限 | 说明 | 类型 |
|------|------|------|
| `im:chat:readonly` | 读取群列表和群信息 | tenant |
| `im:message.group_msg` | 读取群消息 | tenant |
| `im:message:send_as_bot` | 以机器人身份发消息 | tenant |

### 云文档权限

| 权限 | 说明 | 类型 |
|------|------|------|
| `docx:document` | 创建/写入文档 | tenant |
| `docx:document:readonly` | 读取新版文档 | user (OAuth) |
| `docs:doc:readonly` | 读取旧版文档 | user (OAuth) |
| `sheets:spreadsheet:readonly` | 读取电子表格 | user (OAuth) |
| `bitable:app:readonly` | 读取多维表格 | user (OAuth) |
| `wiki:wiki:readonly` | 读取知识库 | user (OAuth) |
| `drive:drive` | 上传文件到云盘 | tenant |

### 其他可选权限

| 权限 | 用途 |
|------|------|
| `contact:user.base:readonly` | 查询用户信息 |
| `sheets:spreadsheet` | 写入电子表格 |
| `calendar:calendar:readonly` | 读取日程 |
| `calendar:calendar` | 创建/修改日程 |

---

## 故障排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Bot ability is not activated` (232025) | 应用未启用机器人能力 | Lark 开放平台 → Features → Bot → 启用 |
| `Bot/User can NOT be out of the chat` (230002) | 机器人未加入群组 | 群设置 → Bots → Add Bot |
| `Lack of necessary permissions` (230027) | 缺少 API 权限 | 开放平台 → Permissions → 开通对应权限 |
| `Access denied...send_as_bot` (99991672) | 缺少发消息权限 | 开通 `im:message:send_as_bot` |
| `Operator and chat can NOT be in different tenants` (232010) | App ID 与群不在同一租户 | 检查 .mcp.json 中的 App ID 是否正确 |
| `no folder permission` (1770040) | 应用无目录写入权限 | 目录链接分享设为「组织内可编辑」 |
| `授权超时` (OAuth) | 2分钟内未完成浏览器授权 | 重新运行脚本，及时完成授权 |
| MCP 工具不可用 | MCP Server 未启动 | 重启 Claude Code，检查 .mcp.json |

---

## 配置变更指南

### 更换 Lark 应用

编辑 `~/.claude/.mcp.json`：
```json
{
  "mcpServers": {
    "lark": {
      "env": {
        "LARK_APP_ID": "新的APP_ID",
        "LARK_APP_SECRET": "新的APP_SECRET"
      }
    }
  }
}
```
然后重启 Claude Code。

### 添加新群组

1. 在 Lark 群中添加机器人
2. 运行 `lark_list_chats` 获取新群的 chat_id
3. 更新本文件的"已连接群组"表

### 扩展 MCP Server

MCP Server 代码位置：
```
~/.claude/plugins/cache/sparticle-skill-marketplace/lark-demand-collector/1.0.0/mcp-server/src/lark_mcp_server/
├── server.py      # 工具定义和请求路由
├── lark_client.py # Lark API 调用实现
```

添加新工具步骤：
1. 在 `lark_client.py` 中添加 API 调用方法
2. 在 `server.py` 的 `list_tools()` 中注册工具定义
3. 在 `server.py` 的 `call_tool()` 中添加处理逻辑
4. 重启 Claude Code 生效

注意：`lark_oapi` 库的 response.data 可能为 None，需用 `response.raw.content` 解析 JSON 作为兜底。
