#!/usr/bin/env python3
"""
AI 模型过期监控脚本
监控 OpenAI、Anthropic、Google Gemini、AWS Bedrock 等厂商的模型生命周期变更，
对比项目中使用的模型清单，提前预警即将停用的模型。

Usage:
    python monitor_model_deprecations.py                          # 基础检查
    python monitor_model_deprecations.py --config models.json     # 对比项目模型
    python monitor_model_deprecations.py --notify                 # 发送通知
    python monitor_model_deprecations.py --format json            # JSON 输出
    python monitor_model_deprecations.py --output report.json     # 保存到文件
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    sys.exit(1)


# ============================================================
# 配置常量
# ============================================================

DEPRECATIONS_FEED_URL = "https://deprecations.info/v1/feed.json"
DEPRECATIONS_RAW_URL = "https://raw.githubusercontent.com/leblancfg/deprecations-rss/main/data.json"

PROVIDER_API_URLS = {
    "openai": "https://api.openai.com/v1/models",
    "anthropic": "https://api.anthropic.com/v1/models",
    "google": "https://generativelanguage.googleapis.com/v1/models",
}

DEPRECATION_PAGES = {
    "OpenAI": "https://platform.openai.com/docs/deprecations",
    "Anthropic": "https://docs.anthropic.com/en/docs/about-claude/model-deprecations",
    "Google": "https://ai.google.dev/gemini-api/docs/deprecations",
    "Azure OpenAI": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-retirements",
}

DEFAULT_THRESHOLDS = {
    "critical_days": 7,
    "warning_days": 30,
    "info_days": 60,
}

TIMEOUT = 30


# ============================================================
# 数据采集
# ============================================================

def fetch_deprecations_info():
    """从 deprecations.info 获取所有厂商的模型过期信息"""
    try:
        resp = requests.get(DEPRECATIONS_FEED_URL, timeout=TIMEOUT)
        resp.raise_for_status()
        feed = resp.json()
    except Exception:
        try:
            resp = requests.get(DEPRECATIONS_RAW_URL, timeout=TIMEOUT)
            resp.raise_for_status()
            feed = resp.json()
        except Exception as e:
            print(f"⚠️  deprecations.info 不可用: {e}")
            return []

    deprecations = []
    for item in feed.get("items", []):
        tags = item.get("tags", [])
        dep_info = item.get("_deprecation", {})
        deprecations.append({
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "content": item.get("content_text", item.get("content_html", "")),
            "date_published": item.get("date_published", ""),
            "tags": tags,
            "url": item.get("external_url", item.get("url", "")),
            "provider": dep_info.get("provider", _extract_provider(tags)),
            # Structured deprecation data from _deprecation field
            "model_id": dep_info.get("model_id", ""),
            "model_name": dep_info.get("model_name", ""),
            "shutdown_date": dep_info.get("shutdown_date", ""),
            "announcement_date": dep_info.get("announcement_date", ""),
            "replacement_models": dep_info.get("replacement_models", []),
        })
    return deprecations


def _extract_provider(tags):
    """从标签中提取厂商名"""
    mapping = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "vertex": "Google Vertex AI",
        "bedrock": "AWS Bedrock",
        "azure": "Azure OpenAI",
        "cohere": "Cohere",
        "xai": "xAI",
    }
    for tag in tags:
        for key, value in mapping.items():
            if key in tag.lower():
                return value
    return "Unknown"


def fetch_openai_models():
    """获取 OpenAI 可用模型列表"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY 未设置，跳过 OpenAI API 检查")
        return None
    try:
        resp = requests.get(
            PROVIDER_API_URLS["openai"],
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return [m["id"] for m in data.get("data", [])]
    except Exception as e:
        print(f"⚠️  OpenAI API 调用失败: {e}")
        return None


def fetch_anthropic_models():
    """获取 Anthropic 可用模型列表"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY 未设置，跳过 Anthropic API 检查")
        return None
    try:
        resp = requests.get(
            PROVIDER_API_URLS["anthropic"],
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return [m["id"] for m in data.get("data", [])]
    except Exception as e:
        print(f"⚠️  Anthropic API 调用失败: {e}")
        return None


def fetch_google_models():
    """获取 Google Gemini 可用模型列表"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY 未设置，跳过 Google API 检查")
        return None
    try:
        resp = requests.get(
            f"{PROVIDER_API_URLS['google']}?key={api_key}",
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("models", []):
            name = m.get("name", "")
            # API 返回 "models/gemini-2.0-flash"，去掉前缀
            if name.startswith("models/"):
                name = name[7:]
            models.append(name)
        return models
    except Exception as e:
        print(f"⚠️  Google API 调用失败: {e}")
        return None


def fetch_bedrock_models():
    """获取 AWS Bedrock 模型及生命周期状态"""
    try:
        import boto3
    except ImportError:
        print("⚠️  boto3 未安装，跳过 AWS Bedrock 检查 (pip install boto3)")
        return None

    try:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        bedrock = boto3.client("bedrock", region_name=region)
        response = bedrock.list_foundation_models()

        results = []
        for model in response.get("modelSummaries", []):
            status = model.get("modelLifecycle", {}).get("status", "UNKNOWN")
            results.append({
                "model_id": model["modelId"],
                "model_name": model.get("modelName", ""),
                "provider": model.get("providerName", ""),
                "status": status,
            })
        return results
    except Exception as e:
        print(f"⚠️  AWS Bedrock API 调用失败: {e}")
        return None


def fetch_all_available_models():
    """获取所有厂商可用模型"""
    available = {}

    openai_models = fetch_openai_models()
    if openai_models is not None:
        available["OpenAI"] = openai_models

    anthropic_models = fetch_anthropic_models()
    if anthropic_models is not None:
        available["Anthropic"] = anthropic_models

    google_models = fetch_google_models()
    if google_models is not None:
        available["Google"] = google_models

    bedrock_models = fetch_bedrock_models()
    if bedrock_models is not None:
        available["AWS Bedrock"] = [m["model_id"] for m in bedrock_models]
        available["bedrock_lifecycle"] = bedrock_models

    return available


# ============================================================
# 分析 & 对比
# ============================================================

DATE_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2})",
    r"(\w+ \d{1,2},?\s*\d{4})",
    r"(\d{1,2}/\d{1,2}/\d{4})",
]


def _parse_shutdown_date(dep_item):
    """尝试从过期信息中解析停用日期"""
    text = dep_item.get("content", "") + " " + dep_item.get("title", "")

    # 查找 shutdown/sunset/retirement/end of life 后面的日期
    shutdown_keywords = r"(?:shutdown|sunset|retire|end.of.life|deprecated|removed|unavailable|停用|下线)"
    for pattern in DATE_PATTERNS:
        match = re.search(rf"{shutdown_keywords}.*?{pattern}", text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            for fmt in ("%Y-%m-%d", "%B %d, %Y", "%B %d %Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

    # 退而求其次：找文本中任何日期
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            for fmt in ("%Y-%m-%d", "%B %d, %Y", "%B %d %Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

    return None


def compare_models(models_in_use, deprecation_data, available_models, thresholds=None):
    """对比项目使用模型与过期信息，生成告警"""
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    alerts = []
    now = datetime.now()

    for model in models_in_use:
        model_id = model["model_id"]
        provider = model.get("provider", "Unknown")

        # 检查 1：模型是否还在可用列表中
        if provider in available_models:
            provider_models = available_models[provider]
            # 进行模糊匹配：精确匹配或前缀匹配
            found = any(
                model_id == m or model_id in m or m in model_id
                for m in provider_models
            )
            if not found:
                alerts.append({
                    "level": "CRITICAL",
                    "model": model_id,
                    "provider": provider,
                    "usage": model.get("usage", ""),
                    "config": model.get("config_location", ""),
                    "message": f"模型 {model_id} 已不在 {provider} 可用模型列表中，可能已停用！",
                    "action": f"立即更换为可用模型，参考 {DEPRECATION_PAGES.get(provider, '')}",
                    "source_url": DEPRECATION_PAGES.get(provider, ""),
                })

        # 检查 2：是否在 deprecations.info 过期列表中
        for dep in deprecation_data:
            dep_model_id = dep.get("model_id", "")

            # 优先使用结构化的 model_id 进行精确匹配
            matched = False
            if dep_model_id:
                matched = (
                    model_id.lower() == dep_model_id.lower()
                    or model_id.lower() in dep_model_id.lower()
                    or dep_model_id.lower() in model_id.lower()
                )
            else:
                # 回退到文本匹配
                dep_text = (dep.get("content", "") + " " + dep.get("title", "")).lower()
                matched = model_id.lower() in dep_text

            if not matched:
                continue

            # 优先使用结构化的 shutdown_date
            shutdown_date = None
            if dep.get("shutdown_date"):
                try:
                    shutdown_date = datetime.strptime(dep["shutdown_date"], "%Y-%m-%d")
                except ValueError:
                    pass
            if not shutdown_date:
                shutdown_date = _parse_shutdown_date(dep)

            replacement = dep.get("replacement_models", [])
            replacement_str = " -> " + ", ".join(replacement) if replacement else ""

            if shutdown_date:
                days_until = (shutdown_date - now).days
                if days_until < 0:
                    level = "CRITICAL"
                    message = f"模型 {model_id} 已于 {shutdown_date.strftime('%Y-%m-%d')} 停用！{replacement_str}"
                elif days_until <= thresholds["critical_days"]:
                    level = "CRITICAL"
                    message = f"模型 {model_id} 将在 {days_until} 天后停用（{shutdown_date.strftime('%Y-%m-%d')}）{replacement_str}"
                elif days_until <= thresholds["warning_days"]:
                    level = "WARNING"
                    message = f"模型 {model_id} 将在 {days_until} 天后停用（{shutdown_date.strftime('%Y-%m-%d')}）{replacement_str}"
                elif days_until <= thresholds["info_days"]:
                    level = "INFO"
                    message = f"模型 {model_id} 将在 {days_until} 天后停用（{shutdown_date.strftime('%Y-%m-%d')}）{replacement_str}"
                else:
                    level = "INFO"
                    message = f"模型 {model_id} 计划于 {shutdown_date.strftime('%Y-%m-%d')} 停用（{days_until} 天后）{replacement_str}"

                alerts.append({
                    "level": level,
                    "model": model_id,
                    "provider": provider,
                    "usage": model.get("usage", ""),
                    "config": model.get("config_location", ""),
                    "shutdown_date": shutdown_date.isoformat(),
                    "days_until_shutdown": days_until,
                    "message": message,
                    "replacement_models": replacement,
                    "source_url": dep.get("url", ""),
                    "action": _suggest_action(level, provider),
                })
            else:
                # 有过期信息但无法解析日期
                alerts.append({
                    "level": "WARNING",
                    "model": model_id,
                    "provider": provider,
                    "usage": model.get("usage", ""),
                    "config": model.get("config_location", ""),
                    "message": f"模型 {model_id} 出现在过期信息中: {dep.get('title', '')}",
                    "source_url": dep.get("url", ""),
                    "action": "请检查官方文档确认停用日期",
                })

        # 检查 3：AWS Bedrock 生命周期状态
        if provider == "AWS Bedrock" and "bedrock_lifecycle" in available_models:
            for bm in available_models["bedrock_lifecycle"]:
                if bm["model_id"] == model_id:
                    if bm["status"] == "LEGACY":
                        alerts.append({
                            "level": "WARNING",
                            "model": model_id,
                            "provider": provider,
                            "usage": model.get("usage", ""),
                            "config": model.get("config_location", ""),
                            "message": f"Bedrock 模型 {model_id} 状态为 LEGACY（即将停用，至少 6 个月缓冲期）",
                            "action": "制定迁移计划，测试替代模型",
                        })
                    elif bm["status"] == "EOL":
                        alerts.append({
                            "level": "CRITICAL",
                            "model": model_id,
                            "provider": provider,
                            "usage": model.get("usage", ""),
                            "config": model.get("config_location", ""),
                            "message": f"Bedrock 模型 {model_id} 已停用 (EOL)！",
                            "action": "立即更换为 ACTIVE 状态的模型",
                        })

    # 去重（同一模型可能被多个数据源命中）
    seen = set()
    unique_alerts = []
    for alert in alerts:
        key = (alert["model"], alert["provider"], alert["level"])
        if key not in seen:
            seen.add(key)
            unique_alerts.append(alert)

    # 按严重程度排序
    priority = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    return sorted(unique_alerts, key=lambda x: priority.get(x["level"], 3))


def _suggest_action(level, provider):
    """根据告警级别建议操作"""
    if level == "CRITICAL":
        return f"立即更换模型，参考 {provider} 官方迁移指南"
    elif level == "WARNING":
        return "在 7 天内制定迁移计划，测试替代模型"
    else:
        return "纳入下一个 Sprint 的技术债务清理"


# ============================================================
# 报告生成
# ============================================================

def generate_markdown_report(project_name, alerts, deprecation_data, available_models):
    """生成 Markdown 格式的预警报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    critical = [a for a in alerts if a["level"] == "CRITICAL"]
    warnings = [a for a in alerts if a["level"] == "WARNING"]
    infos = [a for a in alerts if a["level"] == "INFO"]

    lines = [
        "=" * 60,
        "  AI 模型过期预警报告",
        f"  项目：{project_name}",
        f"  检查时间：{now}",
        "=" * 60,
        "",
    ]

    if critical:
        lines.append("[CRITICAL] 紧急告警 - 需立即处理")
        lines.append("-" * 60)
        for i, a in enumerate(critical, 1):
            lines.append(f"{i}. {a['model']} ({a['provider']})")
            if a.get("usage"):
                lines.append(f"   用途：{a['usage']}")
            if a.get("config"):
                lines.append(f"   配置位置：{a['config']}")
            lines.append(f"   状态：{a['message']}")
            lines.append(f"   建议：{a.get('action', '')}")
            if a.get("source_url"):
                lines.append(f"   参考：{a['source_url']}")
            lines.append("")
    else:
        lines.append("[CRITICAL] 无紧急告警")
        lines.append("")

    if warnings:
        lines.append("[WARNING] 警告 - 30天内过期")
        lines.append("-" * 60)
        for i, a in enumerate(warnings, 1):
            lines.append(f"{i}. {a['model']} ({a['provider']})")
            if a.get("usage"):
                lines.append(f"   用途：{a['usage']}")
            lines.append(f"   状态：{a['message']}")
            lines.append(f"   建议：{a.get('action', '')}")
            lines.append("")
    else:
        lines.append("[WARNING] 无警告")
        lines.append("")

    if infos:
        lines.append("[INFO] 提醒 - 60天内过期")
        lines.append("-" * 60)
        for i, a in enumerate(infos, 1):
            lines.append(f"{i}. {a['model']} ({a['provider']})")
            if a.get("usage"):
                lines.append(f"   用途：{a['usage']}")
            lines.append(f"   状态：{a['message']}")
            lines.append("")

    # 最新过期信息摘要
    lines.append("=" * 60)
    lines.append("  最新模型过期信息（来自 deprecations.info）")
    lines.append("-" * 60)
    # 按停用日期排序，优先显示即将停用的
    upcoming = sorted(
        [d for d in deprecation_data if d.get("shutdown_date")],
        key=lambda x: x["shutdown_date"],
    )
    # 只显示未来即将停用的（或最近停用的）
    now_str = datetime.now().strftime("%Y-%m-%d")
    relevant = [d for d in upcoming if d["shutdown_date"] >= now_str][:15]
    if not relevant:
        relevant = upcoming[-10:]  # 如果没有未来的，显示最近的

    for d in relevant:
        model_name = d.get("model_id") or d.get("model_name") or d.get("id", "")
        replacement = d.get("replacement_models", [])
        rep_str = f" -> {', '.join(replacement)}" if replacement else ""
        lines.append(f"  [{d['provider']}] {model_name}")
        lines.append(f"    停用日期：{d['shutdown_date']}{rep_str}")
        lines.append("")

    # 统计
    lines.append("=" * 60)
    lines.append("  统计摘要")
    lines.append("-" * 60)
    lines.append(f"  紧急告警(CRITICAL)：{len(critical)}")
    lines.append(f"  警告(WARNING)：{len(warnings)}")
    lines.append(f"  提醒(INFO)：{len(infos)}")
    for provider, models in available_models.items():
        if provider != "bedrock_lifecycle" and isinstance(models, list):
            lines.append(f"  {provider} 可用模型数：{len(models)}")
    lines.append("=" * 60)

    # 处理建议
    if critical or warnings:
        lines.append("")
        lines.append("  处理建议")
        lines.append("-" * 60)
        if critical:
            lines.append(f"  1. 优先处理 {len(critical)} 个 CRITICAL 告警，避免线上故障")
        if warnings:
            lines.append(f"  2. 在本周内制定 {len(warnings)} 个 WARNING 模型的迁移计划")
        lines.append("  3. 更新 models_in_use.json 模型清单配置")
        lines.append("  4. 建议设置每日定时检查（GitHub Actions / crontab）")
        lines.append("=" * 60)

    return "\n".join(lines)


def generate_json_report(project_name, alerts, deprecation_data, available_models):
    """生成 JSON 格式的报告"""
    return {
        "project": project_name,
        "generated_at": datetime.now().isoformat(),
        "alerts": alerts,
        "statistics": {
            "critical_count": len([a for a in alerts if a["level"] == "CRITICAL"]),
            "warning_count": len([a for a in alerts if a["level"] == "WARNING"]),
            "info_count": len([a for a in alerts if a["level"] == "INFO"]),
        },
        "deprecation_feed_items": len(deprecation_data),
        "available_models": {
            k: len(v) if isinstance(v, list) else len(v)
            for k, v in available_models.items()
            if k != "bedrock_lifecycle"
        },
    }


# ============================================================
# 通知发送
# ============================================================

def send_slack(webhook_url, alerts, project_name):
    """发送 Slack 通知"""
    critical = [a for a in alerts if a["level"] == "CRITICAL"]
    warnings = [a for a in alerts if a["level"] == "WARNING"]

    if not critical and not warnings:
        return

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"AI Model Deprecation Alert - {project_name}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*CRITICAL*: {len(critical)} | *WARNING*: {len(warnings)}",
            },
        },
    ]

    for alert in (critical + warnings)[:10]:
        emoji = ":rotating_light:" if alert["level"] == "CRITICAL" else ":warning:"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{alert['model']}* ({alert['provider']})\n{alert['message']}\nUsage: {alert.get('usage', 'N/A')}",
            },
        })

    try:
        requests.post(webhook_url, json={"blocks": blocks}, timeout=TIMEOUT)
        print("✅ Slack 通知已发送")
    except Exception as e:
        print(f"❌ Slack 通知发送失败: {e}")


def send_lark(webhook_url, alerts, project_name):
    """发送飞书通知"""
    critical = [a for a in alerts if a["level"] == "CRITICAL"]
    warnings = [a for a in alerts if a["level"] == "WARNING"]

    if not critical and not warnings:
        return

    content = f"**项目：{project_name}**\n\n"
    if critical:
        content += "🚨 **紧急告警**：\n"
        for a in critical:
            content += f"- **{a['model']}** ({a['provider']}): {a['message']}\n"
    if warnings:
        content += "\n⚠️ **警告**：\n"
        for a in warnings:
            content += f"- **{a['model']}** ({a['provider']}): {a['message']}\n"

    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "AI 模型过期预警"},
                "template": "red" if critical else "orange",
            },
            "elements": [{"tag": "markdown", "content": content}],
        },
    }

    try:
        requests.post(webhook_url, json=data, timeout=TIMEOUT)
        print("✅ 飞书通知已发送")
    except Exception as e:
        print(f"❌ 飞书通知发送失败: {e}")


def send_lark_report(webhook_url, alerts, deprecation_data, project_name):
    """发送完整的飞书周报（包含所有级别的告警和即将过期模型摘要）"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    critical = [a for a in alerts if a["level"] == "CRITICAL"]
    warnings = [a for a in alerts if a["level"] == "WARNING"]
    infos = [a for a in alerts if a["level"] == "INFO"]

    # 构建卡片元素
    elements = []

    # 概览
    summary = f"📅 **报告日期**：{date_str}\n"
    summary += f"📊 **项目**：{project_name}\n"
    summary += f"🚨 紧急：**{len(critical)}** 个  ⚠️ 警告：**{len(warnings)}** 个  ℹ️ 提醒：**{len(infos)}** 个"
    elements.append({"tag": "markdown", "content": summary})
    elements.append({"tag": "hr"})

    # CRITICAL
    if critical:
        content = "**🚨 紧急告警（7天内停用或已停用）**\n"
        for a in critical:
            replacement = ""
            if a.get("replacement_models"):
                replacement = f" → {', '.join(a['replacement_models'])}"
            content += f"- **{a['model']}** ({a['provider']}){replacement}\n"
            content += f"  {a['message']}\n"
            if a.get("usage"):
                content += f"  用途：{a['usage']}\n"
        elements.append({"tag": "markdown", "content": content})
        elements.append({"tag": "hr"})

    # WARNING
    if warnings:
        content = "**⚠️ 警告（30天内停用）**\n"
        for a in warnings:
            content += f"- **{a['model']}** ({a['provider']}): {a['message']}\n"
        elements.append({"tag": "markdown", "content": content})
        elements.append({"tag": "hr"})

    # INFO
    if infos:
        content = "**ℹ️ 提醒（60天内停用）**\n"
        for a in infos[:10]:
            content += f"- **{a['model']}** ({a['provider']}): {a['message']}\n"
        if len(infos) > 10:
            content += f"- ... 及其他 {len(infos) - 10} 个\n"
        elements.append({"tag": "markdown", "content": content})
        elements.append({"tag": "hr"})

    # 即将过期的热门模型（来自 deprecations.info，不限于项目使用模型）
    upcoming = sorted(
        [d for d in deprecation_data if d.get("shutdown_date") and d["shutdown_date"] >= date_str],
        key=lambda x: x["shutdown_date"],
    )[:10]
    if upcoming:
        content = "**📋 近期过期模型一览（全行业）**\n"
        for d in upcoming:
            model_name = d.get("model_id") or d.get("model_name") or d.get("title", "")
            rep = d.get("replacement_models", [])
            rep_str = f" → {', '.join(rep)}" if rep else ""
            content += f"- [{d['provider']}] **{model_name}** 停用：{d['shutdown_date']}{rep_str}\n"
        elements.append({"tag": "markdown", "content": content})

    # 操作建议
    if critical or warnings:
        elements.append({"tag": "hr"})
        advice = "**💡 操作建议**\n"
        if critical:
            advice += f"1. 立即处理 {len(critical)} 个 CRITICAL 告警\n"
        if warnings:
            advice += f"2. 本周制定 {len(warnings)} 个 WARNING 模型迁移计划\n"
        advice += "3. 详细报告见 GitHub Actions Artifacts"
        elements.append({"tag": "markdown", "content": advice})

    # 确定卡片颜色
    if critical:
        template = "red"
        title = f"🚨 AI 模型过期周报 - {date_str}"
    elif warnings:
        template = "orange"
        title = f"⚠️ AI 模型过期周报 - {date_str}"
    else:
        template = "green"
        title = f"✅ AI 模型过期周报 - {date_str}"

    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": elements,
        },
    }

    try:
        resp = requests.post(webhook_url, json=data, timeout=TIMEOUT)
        resp.raise_for_status()
        print("✅ 飞书周报已发送")
    except Exception as e:
        print(f"❌ 飞书周报发送失败: {e}")


def send_dingtalk(webhook_url, alerts, project_name):
    """发送钉钉通知"""
    critical = [a for a in alerts if a["level"] == "CRITICAL"]
    warnings = [a for a in alerts if a["level"] == "WARNING"]

    if not critical and not warnings:
        return

    content = f"# AI 模型过期预警 - {project_name}\n\n"
    for a in critical + warnings:
        icon = "🚨" if a["level"] == "CRITICAL" else "⚠️"
        content += f"{icon} **{a['model']}** ({a['provider']})\n"
        content += f"> {a['message']}\n> 用途: {a.get('usage', 'N/A')}\n\n"

    data = {
        "msgtype": "markdown",
        "markdown": {"title": "AI 模型过期预警", "text": content},
    }

    try:
        requests.post(webhook_url, json=data, timeout=TIMEOUT)
        print("✅ 钉钉通知已发送")
    except Exception as e:
        print(f"❌ 钉钉通知发送失败: {e}")


def send_email(smtp_config, recipients, report_text):
    """发送邮件通知"""
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(report_text, "plain", "utf-8")
    msg["Subject"] = "AI Model Deprecation Alert"
    msg["From"] = smtp_config["from"]
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config.get("port", 587)) as server:
            server.starttls()
            server.login(smtp_config.get("username", smtp_config["from"]), smtp_config["password"])
            server.send_message(msg)
        print("✅ 邮件通知已发送")
    except Exception as e:
        print(f"❌ 邮件通知发送失败: {e}")


# ============================================================
# 主流程
# ============================================================

def load_config(config_path):
    """加载配置文件"""
    path = Path(config_path)
    if not path.exists():
        print(f"⚠️  配置文件 {config_path} 不存在，将只显示过期信息")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_check(config_path=None, notify=False, output_format="text", output_file=None, lark_webhook=None):
    """执行模型过期检查"""
    print("🔍 开始检查 AI 模型过期信息...\n")

    # 加载配置
    config = load_config(config_path) if config_path else None
    project_name = config.get("project", "Unknown") if config else "Unknown"
    models_in_use = config.get("models", []) if config else []
    thresholds = config.get("alert_thresholds", DEFAULT_THRESHOLDS) if config else DEFAULT_THRESHOLDS

    # 采集数据
    print("📡 从 deprecations.info 获取过期信息...")
    deprecation_data = fetch_deprecations_info()
    print(f"   获取到 {len(deprecation_data)} 条过期信息\n")

    print("🔗 检查各厂商 API 可用模型...")
    available_models = fetch_all_available_models()
    print()

    # 对比分析
    alerts = []
    if models_in_use:
        print(f"📋 对比 {len(models_in_use)} 个项目使用模型...")
        alerts = compare_models(models_in_use, deprecation_data, available_models, thresholds)
    else:
        print("⚠️  未提供项目模型清单，仅展示过期信息摘要")

    # 生成报告
    if output_format == "json":
        report = generate_json_report(project_name, alerts, deprecation_data, available_models)
        report_text = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        report_text = generate_markdown_report(project_name, alerts, deprecation_data, available_models)

    # 输出
    print("\n" + report_text)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\n📄 报告已保存至: {output_file}")

    # 发送通知
    if notify and config:
        notifications = config.get("notifications", {})

        slack_url = notifications.get("slack_webhook") or os.environ.get("SLACK_WEBHOOK_URL")
        if slack_url:
            send_slack(slack_url, alerts, project_name)

        lark_url = notifications.get("lark_webhook") or os.environ.get("LARK_WEBHOOK_URL")
        if lark_url:
            send_lark(lark_url, alerts, project_name)

        dingtalk_url = notifications.get("dingtalk_webhook") or os.environ.get("DINGTALK_WEBHOOK_URL")
        if dingtalk_url:
            send_dingtalk(dingtalk_url, alerts, project_name)

        email_config = notifications.get("email", {})
        if email_config.get("smtp_host") and email_config.get("recipients"):
            send_email(
                {"host": email_config["smtp_host"], "port": email_config.get("smtp_port", 587),
                 "from": email_config["from"], "password": email_config["password"]},
                email_config["recipients"],
                report_text,
            )

    # 发送飞书完整周报（通过 --lark-webhook 参数触发）
    if lark_webhook:
        send_lark_report(lark_webhook, alerts, deprecation_data, project_name)

    # 返回结果供 Lambda 等使用
    return {
        "critical_count": len([a for a in alerts if a["level"] == "CRITICAL"]),
        "warning_count": len([a for a in alerts if a["level"] == "WARNING"]),
        "info_count": len([a for a in alerts if a["level"] == "INFO"]),
        "total_models": len(models_in_use),
        "alerts": alerts,
    }


def main():
    parser = argparse.ArgumentParser(description="AI 模型过期监控脚本")
    parser.add_argument("--config", help="模型清单配置文件路径 (JSON)")
    parser.add_argument("--notify", action="store_true", help="发送通知")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="输出格式")
    parser.add_argument("--output", help="保存报告到文件")
    parser.add_argument("--lark-webhook", help="飞书 Webhook URL，发送完整周报")
    args = parser.parse_args()

    result = run_check(
        config_path=args.config,
        notify=args.notify,
        output_format=args.format,
        output_file=args.output,
        lark_webhook=args.lark_webhook,
    )

    # 如果有 CRITICAL 告警，返回非零退出码（用于 CI/CD）
    if result["critical_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
