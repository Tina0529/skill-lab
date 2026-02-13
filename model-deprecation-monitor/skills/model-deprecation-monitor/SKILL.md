---
name: model-deprecation-monitor
description: AI 模型过期监控与自动提醒系统。监控 OpenAI、Anthropic、Google Gemini、AWS Bedrock、Azure OpenAI 等厂商的模型生命周期变更，对比项目中使用的模型清单，提前预警即将停用的模型，防止线上故障。
version: 1.0.0
triggers:
  - "模型过期"
  - "模型监控"
  - "模型停用"
  - "model deprecation"
  - "model sunset"
  - "model lifecycle"
  - "模型生命周期"
  - "检查模型"
  - "模型预警"
  - "模型提醒"
  - "check model"
  - "monitor model"
---

# AI 模型过期监控与自动提醒系统

监控各大 AI 模型厂商的模型版本迭代和停用信息，对比项目中实际使用的模型，提前发出预警，防止因模型停用导致线上问题。

---

## 核心能力

1. **多源数据采集** - 从 API、官方文档、deprecations.info 聚合数据获取最新模型过期信息
2. **模型清单对比** - 对比项目实际使用的模型与过期信息，精准定位受影响的功能
3. **分级预警** - 按紧急程度（已过期/7天内/30天内/60天内）分级告警
4. **多渠道通知** - 支持控制台报告、邮件、Slack、飞书、钉钉通知
5. **定时自动化** - 支持 crontab / GitHub Actions / AWS Lambda 定时执行

---

## 支持的模型厂商

| 厂商 | 数据来源 | 监控方式 |
|------|---------|---------|
| OpenAI | API + 官方过期页面 + deprecations.info | 模型列表对比 + 过期日期检查 |
| Anthropic (Claude) | API + 官方过期页面 + deprecations.info | 模型列表对比 + 过期日期检查 |
| Google (Gemini) | API + 官方过期页面 + deprecations.info | 模型列表对比 + 过期日期检查 |
| AWS Bedrock | API（含生命周期状态）| modelLifecycle.status 检查 |
| Azure OpenAI | 官方退役页面 + deprecations.info | 过期日期检查 |

---

## 快速开始

### 前置条件

```bash
# 安装 Python 依赖
pip install requests feedparser boto3

# 设置 API Keys（按需设置你使用的厂商）
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."
# AWS Bedrock 使用 ~/.aws/credentials 或环境变量
# export AWS_ACCESS_KEY_ID="..."
# export AWS_SECRET_ACCESS_KEY="..."
# export AWS_DEFAULT_REGION="us-east-1"
```

### 使用方式

**方式 1：直接对话调用（推荐）**

```
/model-deprecation-monitor
```

或直接说：
```
检查我们项目使用的模型是否有过期风险
监控 OpenAI 和 Anthropic 的模型停用信息
帮我生成模型过期预警报告
```

**方式 2：运行 Python 脚本**

```bash
# 基础检查 - 获取所有厂商最新过期信息
python scripts/monitor_model_deprecations.py

# 对比项目使用的模型
python scripts/monitor_model_deprecations.py --config models_in_use.json

# 输出 JSON 格式
python scripts/monitor_model_deprecations.py --format json

# 发送通知
python scripts/monitor_model_deprecations.py --notify
```

---

## 对话流程

### 第一步：确认监控范围

向用户确认以下信息：
1. 需要监控哪些厂商？（OpenAI / Anthropic / Google / AWS Bedrock / Azure / 全部）
2. 项目中使用了哪些模型？（可以提供模型列表、配置文件路径或仓库地址）
3. 预警阈值？（默认：已过期 + 30天内过期 + 60天内过期）
4. 是否需要通知？（控制台输出 / 邮件 / Slack / 飞书 / 钉钉）

### 第二步：采集模型过期数据

#### 数据源 1：deprecations.info（推荐，聚合所有厂商）

```bash
# 获取 JSON Feed
curl -s "https://deprecations.info/v1/feed.json"

# 获取原始数据
curl -s "https://raw.githubusercontent.com/leblancfg/deprecations-rss/main/data.json"
```

解析逻辑：

```python
import requests
from datetime import datetime, timedelta

def fetch_deprecations_info():
    """从 deprecations.info 获取所有厂商的模型过期信息"""
    url = "https://deprecations.info/v1/feed.json"
    resp = requests.get(url, timeout=30)
    feed = resp.json()

    deprecations = []
    for item in feed.get("items", []):
        deprecations.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "content": item.get("content_text", item.get("content_html", "")),
            "date_published": item.get("date_published"),
            "tags": item.get("tags", []),
            "url": item.get("external_url", item.get("url", "")),
            "provider": _extract_provider(item.get("tags", []))
        })
    return deprecations

def _extract_provider(tags):
    """从标签中提取厂商名"""
    provider_map = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "vertex": "Google Vertex AI",
        "bedrock": "AWS Bedrock",
        "cohere": "Cohere",
        "xai": "xAI"
    }
    for tag in tags:
        tag_lower = tag.lower()
        for key, value in provider_map.items():
            if key in tag_lower:
                return value
    return "Unknown"
```

#### 数据源 2：各厂商 API

**OpenAI - 获取可用模型列表**：
```bash
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = sorted([m['id'] for m in data['data']])
for m in models:
    print(m)
"
```

**Anthropic - 获取可用模型列表**：
```bash
curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  "https://api.anthropic.com/v1/models" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('data', []):
    print(f\"{m['id']} ({m.get('display_name', 'N/A')})\")
"
```

**Google Gemini - 获取可用模型列表**：
```bash
curl -s "https://generativelanguage.googleapis.com/v1/models?key=$GOOGLE_API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(f\"{m['name']} - {m.get('displayName', 'N/A')}\")
"
```

**AWS Bedrock - 获取模型及生命周期状态**：
```python
import boto3

def check_bedrock_models():
    """AWS Bedrock 是唯一在 API 中提供生命周期状态的厂商"""
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    response = bedrock.list_foundation_models()

    results = {"active": [], "legacy": [], "eol": []}
    for model in response['modelSummaries']:
        status = model['modelLifecycle']['status']  # ACTIVE / LEGACY / EOL
        info = {
            "model_id": model['modelId'],
            "model_name": model['modelName'],
            "provider": model['providerName'],
            "status": status
        }
        if status == "ACTIVE":
            results["active"].append(info)
        elif status == "LEGACY":
            results["legacy"].append(info)
        else:
            results["eol"].append(info)
    return results
```

#### 数据源 3：官方过期页面（WebFetch 抓取）

```python
# 各厂商官方过期页面 URL
DEPRECATION_PAGES = {
    "OpenAI": "https://platform.openai.com/docs/deprecations",
    "Anthropic": "https://docs.anthropic.com/en/docs/about-claude/model-deprecations",
    "Google": "https://ai.google.dev/gemini-api/docs/deprecations",
    "Azure OpenAI": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-retirements"
}
```

使用 WebFetch 工具抓取这些页面，提取模型名称、过期日期和替代模型信息。

### 第三步：对比项目使用模型

用户可提供模型使用清单，格式如下：

**models_in_use.json 示例**：
```json
{
  "project": "felo-mygpt",
  "models": [
    {
      "model_id": "gpt-4o",
      "provider": "OpenAI",
      "usage": "主聊天功能",
      "priority": "critical",
      "config_location": "mygpt/config/models.py:L45"
    },
    {
      "model_id": "claude-sonnet-4-5-20250929",
      "provider": "Anthropic",
      "usage": "意图识别",
      "priority": "high",
      "config_location": "mygpt/agent/intent.py:L12"
    },
    {
      "model_id": "gemini-2.0-flash",
      "provider": "Google",
      "usage": "RAG 摘要",
      "priority": "medium",
      "config_location": "mygpt/rag/summarizer.py:L30"
    },
    {
      "model_id": "text-embedding-3-small",
      "provider": "OpenAI",
      "usage": "文本向量化",
      "priority": "critical",
      "config_location": "mygpt/rag/embedding.py:L8"
    }
  ]
}
```

对比逻辑：
```python
def compare_models(models_in_use, deprecation_data, available_models):
    """对比项目使用模型与过期信息"""
    alerts = []
    now = datetime.now()

    for model in models_in_use:
        model_id = model["model_id"]
        provider = model["provider"]

        # 检查 1：模型是否还在可用列表中
        if provider in available_models:
            if model_id not in available_models[provider]:
                alerts.append({
                    "level": "CRITICAL",
                    "model": model_id,
                    "provider": provider,
                    "usage": model["usage"],
                    "config": model.get("config_location", ""),
                    "message": f"模型 {model_id} 已不在 {provider} 可用模型列表中！可能已停用。",
                    "action": "立即更换为可用模型"
                })

        # 检查 2：是否在过期列表中
        for dep in deprecation_data:
            if model_id.lower() in dep.get("content", "").lower() or \
               model_id.lower() in dep.get("title", "").lower():
                shutdown_date = _parse_shutdown_date(dep)
                if shutdown_date:
                    days_until = (shutdown_date - now).days
                    if days_until < 0:
                        level = "CRITICAL"
                        message = f"模型 {model_id} 已于 {shutdown_date.strftime('%Y-%m-%d')} 停用！"
                    elif days_until <= 7:
                        level = "CRITICAL"
                        message = f"模型 {model_id} 将在 {days_until} 天后停用！"
                    elif days_until <= 30:
                        level = "WARNING"
                        message = f"模型 {model_id} 将在 {days_until} 天后停用"
                    elif days_until <= 60:
                        level = "INFO"
                        message = f"模型 {model_id} 将在 {days_until} 天后停用"
                    else:
                        level = "INFO"
                        message = f"模型 {model_id} 计划于 {shutdown_date.strftime('%Y-%m-%d')} 停用"

                    alerts.append({
                        "level": level,
                        "model": model_id,
                        "provider": provider,
                        "usage": model["usage"],
                        "config": model.get("config_location", ""),
                        "shutdown_date": shutdown_date.isoformat() if shutdown_date else None,
                        "days_until_shutdown": days_until,
                        "message": message,
                        "source_url": dep.get("url", ""),
                        "action": _suggest_action(level, provider, model_id)
                    })

        # 检查 3：AWS Bedrock 特殊检查（生命周期状态）
        if provider == "AWS Bedrock" and "bedrock_lifecycle" in available_models:
            for bm in available_models["bedrock_lifecycle"]:
                if bm["model_id"] == model_id and bm["status"] == "LEGACY":
                    alerts.append({
                        "level": "WARNING",
                        "model": model_id,
                        "provider": provider,
                        "usage": model["usage"],
                        "message": f"Bedrock 模型 {model_id} 状态为 LEGACY（即将停用）",
                        "action": "计划迁移到新版本模型"
                    })

    return sorted(alerts, key=lambda x: {"CRITICAL": 0, "WARNING": 1, "INFO": 2}.get(x["level"], 3))

def _suggest_action(level, provider, model_id):
    """根据告警级别建议操作"""
    if level == "CRITICAL":
        return f"立即更换 {model_id}，参考 {provider} 官方迁移指南"
    elif level == "WARNING":
        return f"在 7 天内制定迁移计划，测试替代模型"
    else:
        return f"纳入下一个 Sprint 的技术债务清理"
```

### 第四步：生成预警报告

**报告模板**：

```
============================================================
  AI 模型过期预警报告
  项目：{project_name}
  检查时间：{timestamp}
============================================================

[CRITICAL] 紧急告警 - 需立即处理
------------------------------------------------------------
1. gpt-4-turbo-2024-04-09 (OpenAI)
   用途：主聊天功能
   配置位置：mygpt/config/models.py:L45
   状态：已于 2025-12-15 停用！
   建议：立即更换为 gpt-4o 或 gpt-4.1
   参考：https://platform.openai.com/docs/deprecations

2. claude-3-5-sonnet-20240620 (Anthropic)
   用途：意图识别
   配置位置：mygpt/agent/intent.py:L12
   状态：将在 5 天后停用（2026-02-11）
   建议：立即更换为 claude-sonnet-4-5-20250929
   参考：https://docs.anthropic.com/en/docs/about-claude/model-deprecations

[WARNING] 警告 - 30天内过期
------------------------------------------------------------
1. gemini-2.0-flash (Google)
   用途：RAG 摘要
   配置位置：mygpt/rag/summarizer.py:L30
   状态：将在 25 天后停用（2026-03-31）
   建议：在 7 天内制定迁移计划，测试 gemini-2.5-flash

[INFO] 提醒 - 60天内过期
------------------------------------------------------------
（无）

============================================================
  统计摘要
------------------------------------------------------------
  检查模型数量：4
  紧急告警(CRITICAL)：2
  警告(WARNING)：1
  提醒(INFO)：0
  安全模型：1
============================================================

  处理建议
------------------------------------------------------------
  1. 优先处理 2 个 CRITICAL 告警，避免线上故障
  2. 在本周内制定 WARNING 模型的迁移计划
  3. 更新 models_in_use.json 配置文件
  4. 建议设置每日定时检查（crontab / GitHub Actions）
============================================================
```

### 第五步：发送通知（可选）

**Slack 通知**：
```python
import requests

def send_slack_notification(webhook_url, report_summary, alerts):
    """发送 Slack 告警通知"""
    critical_count = len([a for a in alerts if a["level"] == "CRITICAL"])
    warning_count = len([a for a in alerts if a["level"] == "WARNING"])

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "AI Model Deprecation Alert"}
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*CRITICAL*: {critical_count} | *WARNING*: {warning_count}"
            }
        }
    ]

    for alert in alerts:
        if alert["level"] in ("CRITICAL", "WARNING"):
            emoji = ":rotating_light:" if alert["level"] == "CRITICAL" else ":warning:"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{alert['model']}* ({alert['provider']})\n{alert['message']}\nUsage: {alert['usage']}"
                }
            })

    requests.post(webhook_url, json={"blocks": blocks})
```

**飞书（Lark）通知**：
```python
def send_lark_notification(webhook_url, alerts):
    """发送飞书告警通知"""
    critical_alerts = [a for a in alerts if a["level"] == "CRITICAL"]
    warning_alerts = [a for a in alerts if a["level"] == "WARNING"]

    content = "**AI 模型过期预警**\n\n"

    if critical_alerts:
        content += "🚨 **紧急告警**：\n"
        for a in critical_alerts:
            content += f"- {a['model']} ({a['provider']}): {a['message']}\n"

    if warning_alerts:
        content += "\n⚠️ **警告**：\n"
        for a in warning_alerts:
            content += f"- {a['model']} ({a['provider']}): {a['message']}\n"

    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "AI 模型过期预警"},
                "template": "red" if critical_alerts else "orange"
            },
            "elements": [
                {"tag": "markdown", "content": content}
            ]
        }
    }

    requests.post(webhook_url, json=data)
```

**钉钉通知**：
```python
def send_dingtalk_notification(webhook_url, alerts):
    """发送钉钉告警通知"""
    content = "# AI 模型过期预警\n\n"
    for a in alerts:
        if a["level"] in ("CRITICAL", "WARNING"):
            icon = "🚨" if a["level"] == "CRITICAL" else "⚠️"
            content += f"{icon} **{a['model']}** ({a['provider']})\n"
            content += f"> {a['message']}\n> 用途: {a['usage']}\n\n"

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "AI 模型过期预警",
            "text": content
        }
    }
    requests.post(webhook_url, json=data)
```

**邮件通知**：
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(smtp_config, recipients, report_html):
    """发送邮件告警"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "AI Model Deprecation Alert"
    msg["From"] = smtp_config["from"]
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(report_html, "html", "utf-8"))

    with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
        server.starttls()
        server.login(smtp_config["username"], smtp_config["password"])
        server.send_message(msg)
```

---

## 自动化部署

### 方案 1：GitHub Actions（推荐）

创建 `.github/workflows/model-deprecation-check.yml`：

```yaml
name: AI Model Deprecation Check

on:
  schedule:
    # 每天北京时间 10:00（UTC 02:00）执行
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  check-deprecations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests feedparser boto3

      - name: Run deprecation check
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          LARK_WEBHOOK_URL: ${{ secrets.LARK_WEBHOOK_URL }}
        run: |
          python scripts/monitor_model_deprecations.py \
            --config models_in_use.json \
            --notify \
            --output report.json

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: deprecation-report-${{ github.run_number }}
          path: report.json
          retention-days: 90

      - name: Create issue on critical alerts
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('report.json', 'utf8'));
            const critical = report.alerts.filter(a => a.level === 'CRITICAL');
            if (critical.length > 0) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `[Alert] ${critical.length} 个模型即将/已经停用`,
                body: critical.map(a => `- **${a.model}** (${a.provider}): ${a.message}`).join('\n'),
                labels: ['urgent', 'model-deprecation']
              });
            }
```

### 方案 2：Crontab

```bash
# 每天早上 10 点检查（适合本地或服务器部署）
0 10 * * * cd /path/to/project && python scripts/monitor_model_deprecations.py --config models_in_use.json --notify >> /var/log/model-deprecation.log 2>&1
```

### 方案 3：AWS Lambda / Fargate

```python
# lambda_handler.py
import json
from monitor_model_deprecations import run_check

def lambda_handler(event, context):
    """AWS Lambda 入口"""
    config_path = event.get("config_path", "models_in_use.json")
    result = run_check(config_path=config_path, notify=True)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "critical_count": result["critical_count"],
            "warning_count": result["warning_count"],
            "total_models": result["total_models"]
        })
    }
```

使用 EventBridge 规则设置定时触发（每天 UTC 02:00）：
```json
{
  "schedule": "cron(0 2 * * ? *)"
}
```

---

## 配置文件

### models_in_use.json（项目使用的模型清单）

```json
{
  "project": "my-project",
  "check_interval_days": 1,
  "alert_thresholds": {
    "critical_days": 7,
    "warning_days": 30,
    "info_days": 60
  },
  "notifications": {
    "slack_webhook": "",
    "lark_webhook": "",
    "dingtalk_webhook": "",
    "email": {
      "smtp_host": "",
      "smtp_port": 587,
      "from": "",
      "password": "",
      "recipients": []
    }
  },
  "providers": ["openai", "anthropic", "google"],
  "models": [
    {
      "model_id": "gpt-4o",
      "provider": "OpenAI",
      "usage": "主聊天功能",
      "priority": "critical",
      "config_location": "src/config/models.py:L45",
      "fallback_model": "gpt-4.1"
    },
    {
      "model_id": "claude-sonnet-4-5-20250929",
      "provider": "Anthropic",
      "usage": "意图识别",
      "priority": "high",
      "config_location": "src/agent/intent.py:L12",
      "fallback_model": "claude-sonnet-4-5-latest"
    }
  ]
}
```

---

## 错误处理

### 错误 1：API Key 未设置

```
⚠️ OPENAI_API_KEY 未设置，跳过 OpenAI API 检查。
仍会从 deprecations.info 获取 OpenAI 过期信息。
```

**处理**：即使缺少某个厂商的 API Key，仍然可以通过 deprecations.info 获取过期信息，只是无法验证模型是否还在可用列表中。

### 错误 2：deprecations.info 不可用

```
⚠️ deprecations.info 不可用，回退到各厂商官方页面抓取
```

**处理**：使用 WebFetch 工具直接抓取各厂商的官方过期页面。

### 错误 3：网络连接问题

```
❌ 网络连接失败，请检查代理设置
```

**处理**：支持 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量。

### 错误 4：模型清单文件不存在

```
⚠️ models_in_use.json 未找到，将只显示所有厂商的过期信息，不进行模型对比。
请创建 models_in_use.json 以获得精准预警。
```

---

## 执行规则

### 规则 1：始终从 deprecations.info 获取最新数据

这是最可靠的聚合数据源，覆盖所有主要厂商，每日自动更新。

### 规则 2：API 检查作为补充验证

调用各厂商 API 列出可用模型，验证项目使用的模型是否还存在。

### 规则 3：AWS Bedrock 特殊处理

Bedrock 是唯一在 API 中提供 `modelLifecycle.status` 的厂商：
- `ACTIVE`：正常
- `LEGACY`：即将停用（至少 6 个月缓冲期）
- `EOL`：已停用

### 规则 4：分级告警

| 级别 | 条件 | 响应时间 |
|------|------|---------|
| CRITICAL | 已过期 或 7天内过期 | 立即处理 |
| WARNING | 30天内过期 | 1周内制定迁移计划 |
| INFO | 60天内过期 | 纳入技术债务清理 |

### 规则 5：报告格式

- 默认输出 Markdown 格式的控制台报告
- `--format json` 输出 JSON 供系统集成
- `--format csv` 输出 CSV 供 Excel 分析
- `--output <file>` 保存到文件

---

## 官方参考链接

| 厂商 | 过期页面 | API 文档 |
|------|---------|---------|
| OpenAI | https://platform.openai.com/docs/deprecations | https://platform.openai.com/docs/api-reference/models/list |
| Anthropic | https://docs.anthropic.com/en/docs/about-claude/model-deprecations | https://docs.anthropic.com/en/api/models-list |
| Google | https://ai.google.dev/gemini-api/docs/deprecations | https://ai.google.dev/api/models |
| AWS Bedrock | https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html | ListFoundationModels API |
| Azure OpenAI | https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-retirements | - |
| deprecations.info | https://deprecations.info/ | https://deprecations.info/v1/feed.json |
