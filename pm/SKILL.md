---
name: pm
description: |
  `/pm` 是 `/pmbook` 的快捷别名。所有 PM 项目管理功能由 pmbook 提供。

  触发条件：用户输入 `/pm` 开头的命令
---

# /pm → /pmbook 别名

`/pm` 是 `/pmbook` 的快捷方式。收到 `/pm` 命令时，将参数原样传递给 `/pmbook` 执行。

## 规则

当用户输入以下命令时，**直接调用对应的 `/pmbook` 命令**，不做任何额外交互：

| 用户输入 | 实际执行 |
|---------|---------|
| `/pm init` | `/pmbook init` |
| `/pm meeting` | `/pmbook meeting` |
| `/pm decision [主题]` | `/pmbook decision [主题]` |
| `/pm track` | `/pmbook track` |
| `/pm risk` | `/pmbook risk` |
| `/pm report [类型]` | `/pmbook report [类型]` |
| `/pm onboard` | `/pmbook onboard` |
| `/pm check` | `/pmbook check` |
| `/pm sync` | `/pmbook sync` |
| `/pm`（无参数） | `/pmbook onboard`（显示项目概览） |

## 执行方式

收到 `/pm xxx` 后，立即使用 Skill 工具调用 `pmbook`，将 `xxx` 作为参数传入。不要重复解析命令，直接委托给 pmbook 处理。
