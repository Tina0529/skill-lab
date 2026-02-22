# PM Playbook

让 AI 成为你的项目助理——记住每次沟通、追踪每个课题、生成每份报告。

## 解决什么问题

| PM 痛点 | 解决方案 |
|---------|---------|
| "之前不是说好了吗？" | 沟通记忆：会议纪要自动结构化 |
| "这个课题怎么没人跟？" | 进度追踪：Action Items + 逾期提醒 |
| "周报又得写到几点？" | 报告生成：从记忆自动生成周报/月报 |
| "这个项目的背景是？" | 一键 onboard：项目全貌速览 |

## 命令一览

| 命令 | 作用 |
|------|------|
| `/pmbook init` | 初始化项目 PM 记忆 |
| `/pmbook meeting` | 会议纪要 + 提取 Action Items（最核心） |
| `/pmbook decision [主题]` | 记录重要决策的背景和原因 |
| `/pmbook track` | 查看所有课题和待办状态 |
| `/pmbook risk` | 查看和更新风险清单 |
| `/pmbook report [weekly\|monthly]` | 从记忆自动生成报告 |
| `/pmbook onboard` | 项目快速了解 |
| `/pmbook check` | PM 实践健康度检查 |
| `/pmbook sync` | 检测项目变化，同步记忆 |

> `/pm` 是 `/pmbook` 的快捷别名，功能完全相同。

## 记忆结构

```
project/
└── .pm/
    ├── MEMORY.md        # 项目总览 + 索引（< 150 行）
    ├── meetings/        # 会议纪要
    ├── decisions/       # 决策记录
    ├── actions.md       # Action Items 清单
    └── archive.md       # 归档（自动生成）
```

## 快速开始

```
# 1. 初始化
/pmbook init

# 2. 开完会后口述内容，AI 自动整理
/pmbook meeting
> 刚和客户张总开完会，他说3月必须上线第一版，功能可以砍但登录和搜索必须有...

# 3. 查看待办
/pmbook track

# 4. 生成周报
/pmbook report weekly
```

## 核心特性

- **三层信息模型 (L0/L1/L2)**：每个文件内含摘要 → 结论 → 详情三层，按需逐层读取，节省 token
- **Action Items 去重**：新增会议提取的待办会自动与现有清单比较，避免重复
- **风险主动提醒**：里程碑前 2 周、新决策时、连续 2 周未更新时自动提醒
- **记忆自动压缩**：MEMORY.md 保持 < 150 行，超龄事项自动归档
- **里程碑复盘**：每个里程碑完成时触发简要复盘，积累教训
- **变更同步**：新会话开始时检测项目变化，提示同步记忆

## 设计原则

- **记忆 > 文档**：不是写文档，是让 AI 帮你记住上下文
- **自动更新 > 靠自觉**：明确的触发规则，不依赖人工判断
- **一次一问**：引导式交互，先给建议再确认
- **轻量起步**：只用 `/pmbook meeting` 就能开始

## 安装

将 `SKILL.md` 放入 Claude Code skills 目录：

```bash
mkdir -p ~/.claude/skills/pmbook
cp SKILL.md ~/.claude/skills/pmbook/

# 可选：安装 /pm 快捷别名
mkdir -p ~/.claude/skills/pm
cp ../pm/SKILL.md ~/.claude/skills/pm/
```

## License

MIT
