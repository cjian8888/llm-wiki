---
id: "init-chronicle-trigger"
title: "Init Chronicle Trigger"
type: source_summary
tags:
  - 指针模式记忆
  - 上下文污染
  - 容器化监听
created: "2026-04-06"
updated: "2026-04-06"
source_file: "inbox/init-chronicle-trigger.md"
source_url: ""
source_title: "Init Chronicle Trigger"
source_author: ""
source_date: ""
source_count: 1
status: active
confidence: medium
related: []
---
# Init Chronicle Trigger

本文记录了构建一个高效、自动化的 LLM 知识库的初始化技术流程。核心在于采用“指针模式记忆”来管理上下文，避免信息过载，并升级到“容器化监听”机制以实现知识的持续积累。整个系统结合了基础设施选型（OrbStack + Docker Compose）和数据处理管道（ingest pipeline），最终形成了一个自动增长的知识系统。

## 关键主张

- 应采用“指针模式记忆”，只保留指向文档的入口，避免将所有规范塞入有限的上下文窗口。
- 知识库的摄入过程必须从“手动脚本”升级到“容器化监听”，以保证知识积累的持续性和自动化。
- 基础设施选型倾向于 OrbStack + Docker Compose，因为它在 macOS 上对文件系统事件依赖的常驻监听场景性能更优。
- 打通的 ingest pipeline 实现了从文件进入 inbox 到 LLM 自动提取、生成标准化笔记并归档原文的全流程自动化。

## 实体

`CLAUDE.md`、`OrbStack`、`Docker Compose`、`Obsidian`、`inbox`、`daemon`

## 核心概念

[[concept/指针模式记忆|指针模式记忆]]、[[concept/上下文污染|上下文污染]]、[[concept/容器化监听|容器化监听]]、[[concept/bind-mount|bind mount]]、[[concept/watchdog|watchdog]]、[[concept/ingest-pipeline|ingest pipeline]]、[[concept/结构化知识提取|结构化知识提取]]

## 开放问题 / 知识盲区

- [ ] （待 Lint 阶段补充）

## 参考来源

- 原始文件：`inbox/init-chronicle-trigger.md`
