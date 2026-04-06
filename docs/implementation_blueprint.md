# LLM Wiki 落地工程规划书

> 基于 Karpathy LLM Wiki 模式的具体工程化实施方案。
> 原始理念文档：`docs/karpathy_design_pattern.md`

---

## 概述

本文档将抽象的 Karpathy 模式翻译为可执行的工程规范。核心思路：**wiki 是一个持续编译的知识产物**，而非查询时临时拼凑的结果。LLM 是唯一的写入者，人类是唯一的策展者。

三层架构对应本项目物理目录：

| 抽象层 | 物理目录 | 可变性 |
|--------|----------|--------|
| Raw Sources | `inbox/` | 只读（摄入后归档） |
| The Wiki | `wiki_nodes/` | LLM 全权写入 |
| The Schema | `CLAUDE.md` + 本文档 | 人机共同演化 |

---

## 一、数据结构定义

### 1.1 Wiki Node 文件命名规范

```
wiki_nodes/{type}/{slug}.md
```

- `type/`：页面类型子目录（见下表）
- `slug`：全小写 kebab-case，稳定且唯一（如 `attention-mechanism`）

| 子目录 | 页面类型 | 说明 |
|--------|----------|------|
| `source_summary/` | 源文档摘要 | 每个 inbox 文件对应一页 |
| `entity/` | 实体页 | 人物、机构、模型、数据集等具名对象 |
| `concept/` | 概念页 | 方法论、技术思想、术语 |
| `synthesis/` | 综合分析 | 跨源归纳，主动构建的洞察 |
| `comparison/` | 对比页 | 两个或多个实体/方法的结构化对比 |
| `query_result/` | 查询结果 | 有价值的问答被归档为独立页面 |

### 1.2 标准 YAML Frontmatter

每个 wiki node 文件**必须**以如下 frontmatter 开头：

```yaml
---
id: "attention-mechanism"           # 与文件名 slug 一致，永久不变
title: "注意力机制 (Attention Mechanism)"
type: concept                       # 见上表类型枚举

# 分类标签（层级用 / 分隔，Dataview 可查询）
tags:
  - deep-learning/transformer
  - architecture/attention
  - nlp/sequence-modeling

# 时间戳（ISO 8601 格式）
created: "2026-04-06"
updated: "2026-04-06"

# 来源溯源
source_url: ""                      # 原始 URL（网络文章时填写）
source_file: "inbox/vaswani2017.md" # inbox 中对应的源文件路径
source_count: 3                     # 累计有多少个源文档贡献了此页内容

# 页面健康状态
status: active                      # draft | active | stale | archived
confidence: high                    # low | medium | high（LLM 对内容准确性的自评）

# 显式关联（slug 列表，补充 [[双向链接]] 之外的语义关系）
related:
  - "transformer-architecture"
  - "self-attention"
  - "multi-head-attention"

# 仅 source_summary 类型填写
source_title: ""                    # 原始文档标题
source_author: ""                   # 作者
source_date: ""                     # 发布日期
---
```

**字段约定说明：**

- `id` 一旦确定不可更改（其他页面的 `[[链接]]` 依赖它）
- `status: stale` 由 Lint 脚本自动标记，表示有更新的源文档可能使此页过时
- `confidence: low` 表示内容来源单一或存在矛盾，需人工复核
- `source_count` 由 Ingest 脚本在每次更新时自动递增

### 1.3 Wiki Node 正文结构模板

```markdown
---
(frontmatter)
---

# {title}

{一句话定义，直接切入核心}

## 核心内容

{主体内容，使用 [[双向链接]] 引用其他节点}

## 关键主张

> [!note] 核心洞察
> {此概念最值得记住的一句话}

- **主张 1**：...（来源：[[source_summary/vaswani2017]]）
- **主张 2**：...

## 与相关概念的区别

| 维度 | 本概念 | [[相关概念]] |
|------|--------|-------------|
| ... | ... | ... |

## 开放问题 / 知识盲区

- [ ] {尚未厘清的问题，供后续 Lint 时填充}

## 参考来源

- [[source_summary/vaswani2017]] — Attention Is All You Need
- [[source_summary/bahdanau2015]] — Neural Machine Translation
```

### 1.4 特殊索引文件

`wiki_nodes/index.md` — **内容目录**，每次 Ingest 后更新：

```markdown
## [2026-04-06] 概念页

| 页面 | 摘要 | 源数量 | 状态 |
|------|------|--------|------|
| [[concept/attention-mechanism]] | Transformer 中的核心计算单元 | 3 | active |
```

`wiki_nodes/log.md` — **操作日志**，追加写入，格式固定：

```
## [2026-04-06] ingest | Vaswani 2017 - Attention Is All You Need
## [2026-04-06] query | 注意力机制与卷积的根本区别是什么？
## [2026-04-07] lint | 全库扫描，发现 3 个孤立页面，补充 7 处双向链接
```

---

## 二、摄入管道 (Ingest Pipeline) 设计

### 2.0 执行态：容器化守护进程架构

本项目**不以手动运行脚本为常态**，而是运行在 OrbStack/Docker 容器化环境中，通过守护进程实现对 `inbox/` 的 24 小时无感静默监听。

#### 架构图

```
宿主机 (macOS / OrbStack)
├── /Volumes/MediaData/LLM_Wiki/     ← 你在 Obsidian 中操作的目录
│   ├── inbox/                       ← 拖入文件即触发摄入
│   ├── wiki_nodes/                  ← 容器写回，Obsidian 实时可见
│   └── ...
│
└── Docker (via docker-compose)
    └── wiki-daemon 容器
        ├── /app  ←→  宿主机目录（bind mount，双向实时同步）
        └── scripts/daemon.py        ← watchdog 守护进程常驻
                │
                │ 检测到 inbox/ 新文件
                ▼
            ingest pipeline（Step 1-7）
```

#### 核心组件

| 文件 | 作用 |
|------|------|
| `Dockerfile` | 基于 `python:3.11-slim`，安装 `watchdog` 等依赖 |
| `docker-compose.yml` | 定义 `wiki-daemon` 服务，挂载宿主机目录到 `/app` |
| `scripts/daemon.py` | watchdog 事件循环，监听 `inbox/`，触发摄入管道 |
| `requirements.txt` | Python 依赖清单（watchdog, anthropic 等） |

#### 工作流程

```
你在 Finder / Obsidian Web Clipper 将文件放入 inbox/
    │
    │（bind mount，近实时同步）
    ▼
容器内 watchdog 检测到 FileCreatedEvent
    │
    ├── 文件扩展名不是 .md/.txt → 忽略
    └── 文件扩展名是 .md/.txt
            │
            ▼
        触发 ingest pipeline（今日：打印日志；后续：完整 LLM 处理）
            │
            ▼
        wiki_nodes/ 更新写回 → Obsidian 图谱实时刷新
```

#### 选择 OrbStack 的原因

- 比 Docker Desktop 启动更快、资源占用更低（macOS 原生虚拟化）
- bind mount 性能接近原生，适合高频文件 I/O 的 watchdog 场景
- 容器内修改的文件即时反映到宿主机，Obsidian 无需任何配置

### 2.1 脚本文件结构

```
scripts/
├── daemon.py           # 守护进程（watchdog 入口，容器常驻）
├── ingest.py           # 摄入管道主入口（由 daemon 调用）
├── lint.py             # 知识网格健康检查（见第三章）
├── lib/
│   ├── __init__.py
│   ├── loader.py       # 多格式源文件加载与归一化
│   ├── llm_client.py   # LLM API 封装（支持 Claude / OpenAI）
│   ├── wiki_writer.py  # Wiki Node 生成与更新
│   └── index_updater.py# index.md 与 log.md 维护
└── config.py           # 路径常量、模型配置
```

### 2.2 Pipeline 全流程（7 步）

```
inbox/ 文件
    │
    ▼
[Step 1] 加载与归一化
    │  loader.py：识别格式（.md/.txt/.pdf/.html）
    │  输出：纯文本 + 元数据（URL、标题、作者）
    ▼
[Step 2] 上下文预读
    │  读取 wiki_nodes/index.md
    │  构建"已知实体列表"与"已知概念列表"
    │  目的：让 LLM 知道哪些页面已存在，避免重复创建
    ▼
[Step 3] LLM 结构化提取
    │  Prompt → LLM 返回 JSON：
    │  {
    │    "summary": "...",
    │    "key_claims": [...],
    │    "entities": [...],      # 新实体或已知实体
    │    "concepts": [...],      # 新概念或已知概念
    │    "contradictions": [...],# 与现有知识的矛盾点
    │    "open_questions": [...] # 此源引发的新问题
    │  }
    ▼
[Step 4] 页面规划
    │  决策树：
    │  ├── 为源文档创建 source_summary 页（必须）
    │  ├── 对每个 entity：存在 → 追加更新，不存在 → 新建
    │  └── 对每个 concept：存在 → 追加更新，不存在 → 新建
    │  输出：待写入操作列表 [{action, path, content_delta}]
    ▼
[Step 5] 写入 Wiki Nodes
    │  wiki_writer.py：
    │  ├── 新建：填充完整 frontmatter + 正文模板
    │  └── 更新：
    │       - 追加新主张到"关键主张"节
    │       - 记录矛盾到"开放问题"节
    │       - source_count += 1，updated = today
    ▼
[Step 6] 双向链接注入
    │  扫描所有刚写入/更新的页面正文
    │  对匹配已知实体/概念名称的文本自动包裹 [[slug]]
    │  （仅注入，不删除已有链接）
    ▼
[Step 7] 索引与日志更新
       index_updater.py：
       ├── 在 index.md 对应分类下插入/更新行
       └── 向 log.md 追加条目
           格式：## [{date}] ingest | {source_title}
```

### 2.3 `ingest.py` 命令行接口设计

```bash
# 摄入单个文件（推荐，保持人工参与）
python scripts/ingest.py inbox/vaswani2017.md

# 摄入并指定源 URL（网络文章场景）
python scripts/ingest.py inbox/article.md --url https://example.com/article

# 批量摄入（低监督模式）
python scripts/ingest.py --batch inbox/

# 演练模式：仅打印将要执行的操作，不写入文件
python scripts/ingest.py inbox/vaswani2017.md --dry-run
```

### 2.4 LLM 提取 Prompt 设计（核心）

```
系统提示：
你是一个严格的知识管理员。你的任务是从原始文档中提取结构化知识，
并将其整合进现有知识库。你必须：
1. 优先更新已有页面，而非无限创建新页面
2. 明确标记新信息与现有知识的矛盾
3. 返回严格的 JSON，不得包含任何其他文字

已知实体（请复用这些 slug，而非新建）：
{existing_entities_list}

已知概念（请复用这些 slug，而非新建）：
{existing_concepts_list}

用户提示：
请分析以下文档，返回 JSON 格式的提取结果：

{document_text}
```

### 2.5 摄入后的人工审核建议

脚本完成后，在终端打印审核清单：

```
✅ 已创建：wiki_nodes/source_summary/vaswani2017.md
✅ 已创建：wiki_nodes/concept/attention-mechanism.md
🔄 已更新：wiki_nodes/concept/transformer-architecture.md（追加 2 条主张）
⚠️  矛盾检测：vaswani2017 的位置编码方案与 shaw2018 存在分歧 → 已记录至开放问题
❓ 新问题：为什么 softmax 前要除以 √d_k？→ 已记录至 attention-mechanism.md

建议审核：
  obsidian://open?vault=LLM_Wiki&file=wiki_nodes/concept/attention-mechanism
```

---

## 三、知识网格 (Linting & Interlinking) 规划

### 3.1 设计哲学

Lint 不是被动的格式检查，而是**主动的知识健康维护**。其目标是让知识库随着规模增长保持内聚性，而非逐渐碎片化。Lint 脚本在两个层面工作：

- **结构层**：纯程序分析，发现图拓扑问题（孤立节点、断链）
- **语义层**：LLM 分析，发现内容矛盾、盲区、过时信息

### 3.2 `lint.py` 全流程

#### Phase 1：构建链接图（程序层）

```python
# 扫描所有 wiki_nodes/**/*.md
# 提取每个文件中的 [[slug]] 引用
# 构建有向图：
#   节点 = wiki node slug
#   有向边 = A 的正文引用了 B（A → B）

graph = {
    "attention-mechanism": {
        "outlinks": ["transformer-architecture", "vaswani2017"],
        "inlinks": ["transformer-architecture", "bert", "gpt2-analysis"]
    },
    ...
}
```

#### Phase 2：结构性问题检测（程序层）

| 检测项 | 判定条件 | 处置方式 |
|--------|----------|----------|
| **孤立页面** | `inlinks == []` | 标记为 `⚠️ orphan`，尝试自动注入链接 |
| **断链** | 被引用的 slug 无对应文件 | 标记为 `❌ broken`，提示创建缺失页面 |
| **无链页面** | `outlinks == []` 且非 source_summary | 标记为 `⚠️ isolated`，提示补充交叉引用 |
| **过时页面** | frontmatter `status == active` 但 `updated` 距今 > 90 天且 source_count < 2 | 自动改 `status: stale` |
| **低置信页面** | `confidence == low` 且创建 > 30 天 | 列入人工复核清单 |

#### Phase 3：语义性问题检测（LLM 层）

将结构分析结果 + 全部页面摘要传给 LLM，执行以下分析：

**3a. 矛盾检测**
```
请阅读以下 wiki 页面摘要，找出任何相互矛盾的主张。
对每处矛盾，指出：(1)矛盾所在的两个页面，(2)矛盾的具体内容，(3)建议的解决方式。
```

**3b. 知识盲区发现**
```
基于现有页面，哪些重要概念被频繁提及但缺少独立页面？
哪些实体之间明显相关但缺少直接链接？
```

**3c. 研究方向建议**
```
基于当前知识库的结构和内容，建议 3-5 个值得深入探索的问题或方向，
以及可能的源文档类型（论文/博客/数据集等）。
```

#### Phase 4：自动双向链接注入

```python
# 对所有 status == active 的页面执行：
# 1. 收集全库已知实体和概念的（title, slug）映射
# 2. 对每个页面正文，扫描是否存在未链接的实体/概念名称
# 3. 自动包裹 [[slug|显示名]] 格式的链接
# 4. 规则：
#    - 同一页面同一 slug 最多注入一次（避免刷屏）
#    - 不在代码块、frontmatter、已有链接内部注入
#    - 注入后 updated 时间戳更新
```

### 3.3 `lint.py` 命令行接口

```bash
# 完整 Lint（结构 + 语义）
python scripts/lint.py

# 仅结构检查（快速，无 LLM 调用）
python scripts/lint.py --struct-only

# 仅自动注入双向链接（不做语义分析）
python scripts/lint.py --interlink-only

# 演练：打印将要注入的链接，不写入
python scripts/lint.py --interlink-only --dry-run

# Lint 报告保存为 wiki 页面（优质分析值得归档）
python scripts/lint.py --save-report
# → 生成 wiki_nodes/synthesis/lint-report-2026-04-07.md
```

### 3.4 Lint 报告格式

```markdown
## [2026-04-07] lint | 全库健康检查

### 结构问题

| 类型 | 数量 | 页面 |
|------|------|------|
| 孤立页面 | 2 | `entity/yann-lecun`, `concept/rlhf` |
| 断链 | 1 | `concept/moe` 引用了不存在的 `concept/sparse-routing` |

### 自动修复

- 注入了 7 处双向链接
- 标记了 3 个页面为 `status: stale`

### 语义发现（LLM 分析）

**矛盾**：`concept/scaling-laws` 与 `source_summary/hoffmann2022` 对最优计算分配的结论存在分歧。
建议：阅读 Chinchilla 论文原文后更新 `scaling-laws` 页面。

**知识盲区**：`concept/mixture-of-experts` 被 4 个页面引用，但尚无独立页面。

**研究建议**：当前知识库对推理效率关注不足，建议摄入 FlashAttention 系列论文。
```

---

## 四、脚本开发优先级

| 优先级 | 脚本 | 依赖 | 说明 |
|--------|------|------|------|
| P0 | `scripts/config.py` | 无 | 路径常量，所有脚本的基础 |
| P0 | `scripts/lib/loader.py` | 无 | 支持 .md/.txt 即可启动 |
| P0 | `scripts/lib/llm_client.py` | anthropic SDK | 先实现 Claude API 调用 |
| P0 | `scripts/ingest.py`（核心流程） | 以上全部 | 先实现 Step 1-5，跳过自动链接 |
| P1 | `scripts/lib/index_updater.py` | ingest.py | 维护 index.md 和 log.md |
| P1 | `scripts/ingest.py`（Step 6 链接注入） | index_updater | 完成完整 pipeline |
| P2 | `scripts/lint.py`（结构层） | ingest.py | 先做图分析，不需要 LLM |
| P3 | `scripts/lint.py`（语义层） | 结构层 lint | 完整 Lint |

---

## 五、约定摘要（Schema 快查）

```
目录约定：
  inbox/          → 源文档投放区，摄入后移至 inbox/archived/
  wiki_nodes/     → LLM 全权写入，人类只读
  wiki_nodes/index.md  → 内容目录，每次 ingest 更新
  wiki_nodes/log.md    → 操作日志，只追加

文件命名：
  wiki_nodes/{type}/{kebab-slug}.md

Frontmatter 必填字段：
  id, title, type, tags, created, updated, status, confidence

链接语法：
  [[slug]]          → 跨页引用（Obsidian 兼容）
  [[slug|显示名]]   → 带别名的引用

日志条目格式：
  ## [{YYYY-MM-DD}] {ingest|query|lint} | {描述}

状态枚举：
  draft → active → stale → archived
```

---

*本文档随知识库演化持续更新。当实际工程与此规划产生分歧时，以实际运行情况为准，并同步修订本文档。*
