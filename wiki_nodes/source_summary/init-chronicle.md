---
id: "init-chronicle"
title: "Init Chronicle"
type: source_summary
tags:
  - RAG 系统
  - LLM Wiki 模式
  - 指针模式记忆
created: "2026-04-06"
updated: "2026-04-06"
source_file: "inbox/init-chronicle.md"
source_url: ""
source_title: "Init Chronicle"
source_author: ""
source_date: ""
source_count: 1
status: active
confidence: medium
related: []
---
# Init Chronicle

本文记录了设计和落地一个完整的 AI 知识库系统的关键技术决策过程，核心在于将知识管理从“文件搜索”升级为“持续编译的结构化大脑”。系统通过指针模式实现按需加载规范、引入守护进程以实现零摩擦自动摄入，并最终构建了基础设施、能力和严格分层的知识三层架构。

## 关键主张

- LLM Wiki 模式的关键在于让知识库成为一个“持续编译的产物”，而非每次查询都在重新发现知识的文件搜索引擎。
- 采用“指针模式记忆”实现了上下文窗口的渐进式披露，确保只有在需要时才加载完整的架构规范文档。
- 引入 `watchdog` 守护进程解决了手动运行脚本带来的维护成本和用户懈怠问题，实现了零摩擦的自动知识积累。
- 系统最终分层为基础设施层（感知与调度）、能力层（数据处理与调用）和知识层（结构化 Markdown 文件）。
- 后续工作重点是让 Lint 脚本自动化补全知识图谱的边，如发现孤立页面和检测语义矛盾。

## 实体

`Andrej Karpathy`、`CLAUDE.md`、`OrbStack`、`Docker Desktop`、`Obsidian`、`Kimi`、`OpenAI`

## 核心概念

[[concept/rag-系统|RAG 系统]]、[[concept/llm-wiki-模式|LLM Wiki 模式]]、[[concept/指针模式记忆|指针模式记忆]]、[[concept/渐进式披露|渐进式披露]]、[[concept/守护进程-watchdog|守护进程 (watchdog)]]、[[concept/零摩擦积累|零摩擦积累]]、[[concept/yaml-frontmatter|YAML Frontmatter]]、[[concept/知识图谱|知识图谱]]

## 开放问题 / 知识盲区

- [ ] （待 Lint 阶段补充）

## 参考来源

- 原始文件：`inbox/init-chronicle.md`
